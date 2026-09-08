"""Operações do laboratório M1.3 implementadas manualmente.

Todas as operações são de vizinhança: o valor de cada pixel de saída depende de
uma região da entrada. O percurso das vizinhanças, o tratamento das bordas e a
combinação com o kernel são explícitos. Nenhuma função pronta de convolução,
filtro de média, Laplaciano, Sobel ou preenchimento de borda é utilizada.

Convenção adotada
-----------------
Os coeficientes do kernel são aplicados na orientação em que estão escritos,
sem giro de 180 graus. Essa é a convenção didática do material da disciplina.
Estritamente, a operação é uma correlação. Para kernels simétricos, como média
e gaussiano, as duas convenções coincidem. Para Sobel, o giro inverteria o
sinal das respostas, mas não a magnitude das bordas.

Notas numéricas
---------------
O acumulador é ``float`` e a resposta bruta é devolvida em ``float64``, que
comporta valores negativos e valores acima de 255. A conversão para 8 bits
acontece somente nas funções de visualização, no fim do processo.
"""

from __future__ import annotations

import math

import numpy as np

from .errors import PdiLabError
from .image_io import channel_count
from .kernels import (
    LAPLACIAN_3X3,
    SOBEL_X_3X3,
    SOBEL_Y_3X3,
    WEIGHTED_MEAN_3X3,
    mean_kernel,
    normalized,
    validate_kernel,
)

# Pesos da luminância na ordem BGR usada pelo OpenCV.
WEIGHT_BLUE = 0.114
WEIGHT_GREEN = 0.587
WEIGHT_RED = 0.299

MAX_VALUE = 255

BORDER_COPY = "copy"
BORDER_REPLICATE = "replicate"
BORDER_STRATEGIES = (BORDER_COPY, BORDER_REPLICATE)

# Deslocamento usado na visualização de respostas com sinal.
VIEW_OFFSET = 128

VIEW_CLAMP = "clamp"
VIEW_ABS = "abs"
VIEW_OFFSET_NAME = "offset"
VIEW_NORMALIZE = "normalize"
VIEWS = (VIEW_CLAMP, VIEW_ABS, VIEW_OFFSET_NAME, VIEW_NORMALIZE)


def _round_half_up(value: float) -> int:
    """Arredonda para o inteiro mais próximo com desempate para cima."""
    return math.floor(value + 0.5)


def _clamp_to_uint8(value: float) -> int:
    """Arredonda e satura o valor no intervalo válido de 8 bits."""
    rounded = _round_half_up(value)
    if rounded < 0:
        return 0
    if rounded > MAX_VALUE:
        return MAX_VALUE
    return rounded


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """Converte para níveis de cinza pela média ponderada da luminância.

    Imagens que já possuem um único canal são devolvidas sem alteração. As
    operações deste laboratório atuam sobre imagens em níveis de cinza, e esta
    função permite que os mesmos comandos aceitem uma entrada colorida.
    """
    if channel_count(image) == 1:
        return image

    height, width = image.shape[0], image.shape[1]
    result = np.zeros((height, width), dtype=np.uint8)

    for y in range(height):
        source_row = image[y].tolist()
        target_row = [0] * width
        for x in range(width):
            blue, green, red = source_row[x]
            luminance = (
                WEIGHT_BLUE * blue + WEIGHT_GREEN * green + WEIGHT_RED * red
            )
            target_row[x] = _clamp_to_uint8(luminance)
        result[y] = target_row

    return result


def _validate_border(border: str) -> str:
    """Valida a estratégia de tratamento de borda."""
    if border not in BORDER_STRATEGIES:
        raise PdiLabError(
            "estrategia de borda invalida: "
            + repr(border)
            + "; use "
            + " ou ".join(BORDER_STRATEGIES)
        )
    return border


def convolve(
    image: np.ndarray,
    kernel: list[list[float]],
    border: str = BORDER_REPLICATE,
) -> np.ndarray:
    """Aplica um kernel quadrado de dimensão ímpar sobre a imagem.

    O centro do kernel é alinhado ao pixel de saída, e a vizinhança percorrida
    vai de ``-raio`` a ``+raio`` nas duas direções.

    Estratégias de borda:

    * ``copy``, os pixels em que a vizinhança não cabe integralmente mantêm o
      valor da entrada;
    * ``replicate``, uma coordenada fora da imagem é substituída pela
      coordenada válida mais próxima.

    Devolve a resposta bruta em ``float64``, sem saturação e sem arredondar.
    """
    validate_kernel(kernel)
    _validate_border(border)

    gray = to_grayscale(image)
    height, width = gray.shape[0], gray.shape[1]
    size = len(kernel)
    radius = size // 2

    rows = gray.tolist()
    result = np.zeros((height, width), dtype=np.float64)

    last_y = height - 1
    last_x = width - 1

    for y in range(height):
        fits_vertically = radius <= y <= last_y - radius
        target_row = [0.0] * width

        for x in range(width):
            fits = fits_vertically and radius <= x <= last_x - radius

            if not fits and border == BORDER_COPY:
                target_row[x] = float(rows[y][x])
                continue

            total = 0.0
            for ky in range(size):
                # Limita a coordenada ao intervalo valido. No interior da
                # imagem a limitacao nao altera nada; na periferia ela realiza
                # a replicacao do pixel mais proximo.
                source_y = y + ky - radius
                if source_y < 0:
                    source_y = 0
                elif source_y > last_y:
                    source_y = last_y

                source_row = rows[source_y]
                kernel_row = kernel[ky]

                for kx in range(size):
                    source_x = x + kx - radius
                    if source_x < 0:
                        source_x = 0
                    elif source_x > last_x:
                        source_x = last_x

                    total += source_row[source_x] * kernel_row[kx]

            target_row[x] = total

        result[y] = target_row

    return result


def mean_filter(
    image: np.ndarray, size: int = 3, border: str = BORDER_REPLICATE
) -> np.ndarray:
    """Filtro de média com janela ``size`` por ``size``.

    Todos os vizinhos têm o mesmo peso, ``1 / (size * size)``.
    """
    return convolve(image, mean_kernel(size), border)


def weighted_mean(
    image: np.ndarray, border: str = BORDER_REPLICATE
) -> np.ndarray:
    """Média ponderada 3 por 3, na aproximação gaussiana do material.

    Os pesos são ``[1 2 1; 2 4 2; 1 2 1]`` divididos por 16, de forma que o
    centro pese mais que os vizinhos ortogonais, que por sua vez pesam mais que
    as diagonais.
    """
    return convolve(image, normalized(WEIGHTED_MEAN_3X3), border)


def laplacian(
    image: np.ndarray, border: str = BORDER_REPLICATE
) -> np.ndarray:
    """Resposta bruta do Laplaciano de 4 vizinhos.

    O kernel usado tem centro ``-4``, portanto a resposta é positiva quando o
    centro é mais escuro que a vizinhança e negativa quando é mais claro. A
    soma dos coeficientes é zero, então uma região constante responde zero.

    O resultado contém valores negativos e é devolvido sem saturação, para que
    possa ser usado no realce antes de qualquer conversão.
    """
    return convolve(image, LAPLACIAN_3X3, border)


def laplacian_enhance(
    image: np.ndarray,
    border: str = BORDER_REPLICATE,
    factor: float = 1.0,
) -> np.ndarray:
    """Realce pela combinação da imagem original com a resposta Laplaciana.

    Aplica ``g = f - fator * L``, com o kernel de centro ``-4``. A subtração é
    o que corresponde a esse sinal: onde o centro é mais claro que a vizinhança
    a resposta é negativa, e subtrair torna o centro ainda mais claro.

    Com ``fator = 1`` a operação equivale ao kernel ``[0 -1 0; -1 5 -1; 0 -1 0]``.

    A combinação usa a resposta bruta. Saturar o Laplaciano antes descartaria a
    metade negativa e arruinaria o realce.
    """
    if isinstance(factor, bool) or not isinstance(factor, (int, float, np.number)):
        raise PdiLabError("fator de realce invalido: " + repr(factor))
    factor = float(factor)
    if not math.isfinite(factor):
        raise PdiLabError("fator de realce invalido: " + repr(factor))

    gray = to_grayscale(image)
    response = laplacian(gray, border)

    height, width = gray.shape[0], gray.shape[1]
    rows = gray.tolist()
    raw_rows = response.tolist()
    result = np.zeros((height, width), dtype=np.uint8)

    for y in range(height):
        source_row = rows[y]
        response_row = raw_rows[y]
        target_row = [0] * width
        for x in range(width):
            target_row[x] = _clamp_to_uint8(
                source_row[x] - factor * response_row[x]
            )
        result[y] = target_row

    return result


def sobel(image: np.ndarray, border: str = BORDER_REPLICATE) -> dict:
    """Calcula as componentes do gradiente e as duas magnitudes.

    Devolve um dicionário com as respostas brutas em ``float64``:

    * ``gx``, variação ao longo de x, que evidencia bordas verticais;
    * ``gy``, variação ao longo de y, que evidencia bordas horizontais;
    * ``l1``, magnitude aproximada ``|Gx| + |Gy|``;
    * ``l2``, magnitude euclidiana ``sqrt(Gx^2 + Gy^2)``.

    Com entrada de 8 bits, cada componente fica entre -1020 e 1020. Nada é
    saturado nem convertido aqui.
    """
    gray = to_grayscale(image)
    gx = convolve(gray, SOBEL_X_3X3, border)
    gy = convolve(gray, SOBEL_Y_3X3, border)

    height, width = gray.shape[0], gray.shape[1]
    l1 = np.zeros((height, width), dtype=np.float64)
    l2 = np.zeros((height, width), dtype=np.float64)

    gx_rows = gx.tolist()
    gy_rows = gy.tolist()

    for y in range(height):
        gx_row = gx_rows[y]
        gy_row = gy_rows[y]
        l1_row = [0.0] * width
        l2_row = [0.0] * width
        for x in range(width):
            horizontal = gx_row[x]
            vertical = gy_row[x]
            l1_row[x] = abs(horizontal) + abs(vertical)
            l2_row[x] = math.sqrt(horizontal * horizontal + vertical * vertical)
        l1[y] = l1_row
        l2[y] = l2_row

    return {"gx": gx, "gy": gy, "l1": l1, "l2": l2}


def to_uint8(raw: np.ndarray, view: str = VIEW_CLAMP) -> np.ndarray:
    """Converte uma resposta bruta em imagem de 8 bits para visualização.

    Modos disponíveis:

    * ``clamp``, arredonda e satura em 0 e 255, preservando a escala absoluta;
    * ``abs``, usa o valor absoluto e depois satura, mostrando a força da
      resposta e descartando o sinal;
    * ``offset``, soma 128 antes de saturar, de forma que 128 represente
      resposta zero, valores menores representem respostas negativas e maiores
      representem positivas;
    * ``normalize``, mapeia a faixa observada para 0 a 255, o que melhora a
      visibilidade e altera a escala absoluta.

    A transformação usada precisa ser declarada, porque a imagem resultante não
    contém mais os valores brutos.
    """
    if view not in VIEWS:
        raise PdiLabError(
            "modo de visualizacao invalido: "
            + repr(view)
            + "; use um entre "
            + ", ".join(VIEWS)
        )

    height, width = raw.shape[0], raw.shape[1]
    rows = raw.tolist()
    result = np.zeros((height, width), dtype=np.uint8)

    if view == VIEW_NORMALIZE:
        lowest = min(min(row) for row in rows)
        highest = max(max(row) for row in rows)
        span = highest - lowest

    for y in range(height):
        source_row = rows[y]
        target_row = [0] * width
        for x in range(width):
            value = source_row[x]
            if view == VIEW_ABS:
                value = abs(value)
            elif view == VIEW_OFFSET_NAME:
                value = value + VIEW_OFFSET
            elif view == VIEW_NORMALIZE:
                value = 0.0 if span == 0 else (value - lowest) * MAX_VALUE / span
            target_row[x] = _clamp_to_uint8(value)
        result[y] = target_row

    return result


def response_summary(raw: np.ndarray, tolerance: float = 1e-9) -> dict:
    """Estatísticas de uma resposta bruta, usadas na análise do relatório.

    As comparações com zero e com os limites de 8 bits usam uma tolerância,
    porque somar nove parcelas de ``255/9`` em ponto flutuante devolve
    255,00000000000003. Sem a tolerância, esse resíduo seria contado como um
    valor fora da faixa, o que não descreve o comportamento do filtro.
    """
    rows = raw.tolist()
    total = 0.0
    count = 0
    lowest = None
    highest = None
    negatives = 0
    zeros = 0
    positives = 0
    outside = 0

    for row in rows:
        for value in row:
            count += 1
            total += value
            if lowest is None or value < lowest:
                lowest = value
            if highest is None or value > highest:
                highest = value
            if value < -tolerance:
                negatives += 1
            elif value <= tolerance:
                zeros += 1
            else:
                positives += 1
            if value < -tolerance or value > MAX_VALUE + tolerance:
                outside += 1

    return {
        "pixels": count,
        "min": lowest,
        "max": highest,
        "mean": total / count,
        "negatives": negatives,
        "zeros": zeros,
        "positives": positives,
        "outside_8bit": outside,
    }
