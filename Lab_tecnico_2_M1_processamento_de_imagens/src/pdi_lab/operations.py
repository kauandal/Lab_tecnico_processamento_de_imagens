"""Operações do laboratório M1.2 implementadas manualmente.

Todas as transformações são pontuais: cada pixel de saída depende apenas do
pixel correspondente da entrada. O percurso é explícito, e nenhuma função
pronta de brilho, contraste, negativo, limiarização ou histograma é utilizada.

Notas numéricas
---------------
Cada linha é convertida para lista Python com ``tolist()`` antes do percurso.
Isso mantém o acesso pixel a pixel e faz as contas com inteiros de precisão
arbitrária ou ponto flutuante do Python, evitando o estouro silencioso que
ocorre ao operar diretamente sobre ``uint8``. A saturação e o arredondamento
acontecem apenas no momento de gravar o valor final.
"""

from __future__ import annotations

import math

import numpy as np

from .errors import PdiLabError
from .image_io import channel_count

# Pesos da luminância na ordem BGR usada pelo OpenCV.
WEIGHT_BLUE = 0.114
WEIGHT_GREEN = 0.587
WEIGHT_RED = 0.299

MAX_VALUE = 255
HISTOGRAM_SIZE = 256

# Ponto fixo da transformação de contraste, no meio da faixa de 8 bits.
CONTRAST_PIVOT = 128


def _round_half_up(value: float) -> int:
    """Arredonda para o inteiro mais próximo com desempate para cima.

    A função ``round`` do Python usa arredondamento bancário, que faria 0,5
    virar 0 e 2,5 virar 2. Aqui o critério é fixo para manter o resultado
    determinístico e igual ao que se calcula à mão.
    """
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

    Aplica ``g = 0,299R + 0,587G + 0,114B``. Imagens que já possuem um único
    canal são devolvidas sem alteração.

    As transformações deste laboratório atuam sobre imagens em níveis de cinza.
    Esta função existe para permitir que os mesmos comandos aceitem uma entrada
    colorida, convertendo antes de transformar.
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


def _map_pixels(image: np.ndarray, transform) -> np.ndarray:
    """Percorre a imagem aplicando ``transform`` a cada pixel.

    O percurso é explícito e o resultado é saturado somente na escrita. O
    parâmetro ``transform`` recebe o valor do pixel como inteiro Python e
    devolve o valor calculado, ainda sem saturação.
    """
    gray = to_grayscale(image)
    height, width = gray.shape[0], gray.shape[1]
    result = np.zeros((height, width), dtype=np.uint8)

    for y in range(height):
        source_row = gray[y].tolist()
        target_row = [0] * width
        for x in range(width):
            target_row[x] = _clamp_to_uint8(transform(source_row[x]))
        result[y] = target_row

    return result


def brightness(image: np.ndarray, value: int) -> np.ndarray:
    """Ajuste de brilho: ``g(x,y) = f(x,y) + b``.

    Valores positivos clareiam e negativos escurecem. O resultado é saturado
    em 0 e em 255, de forma que deslocamentos grandes achatam a imagem contra
    um dos extremos.
    """
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
        raise PdiLabError("valor de brilho invalido: " + repr(value))
    value = int(value)

    return _map_pixels(image, lambda pixel: pixel + value)


def contrast(image: np.ndarray, alpha: float) -> np.ndarray:
    """Ajuste de contraste: ``g(x,y) = alpha * (f(x,y) - 128) + 128``.

    O ponto fixo é 128: pixels com esse valor não mudam. ``alpha`` menor que 1
    aproxima as intensidades do centro e reduz o contraste, ``alpha`` igual a 1
    é a identidade e ``alpha`` maior que 1 afasta as intensidades do centro.
    """
    if isinstance(alpha, bool) or not isinstance(alpha, (int, float, np.number)):
        raise PdiLabError("valor de alpha invalido: " + repr(alpha))
    alpha = float(alpha)
    if not math.isfinite(alpha):
        raise PdiLabError("valor de alpha invalido: " + repr(alpha))
    if alpha < 0:
        raise PdiLabError(
            "valor de alpha invalido: "
            + str(alpha)
            + "; use um numero maior ou igual a zero"
        )

    return _map_pixels(
        image, lambda pixel: alpha * (pixel - CONTRAST_PIVOT) + CONTRAST_PIVOT
    )


def negative(image: np.ndarray) -> np.ndarray:
    """Negativo: ``g(x,y) = 255 - f(x,y)``.

    A operação é sua própria inversa: aplicá-la duas vezes devolve a imagem
    original, sem perda.
    """
    return _map_pixels(image, lambda pixel: MAX_VALUE - pixel)


def threshold(image: np.ndarray, value: int) -> np.ndarray:
    """Limiarização binária.

    Devolve 255 quando o pixel é maior ou igual ao limiar e 0 caso contrário.
    """
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
        raise PdiLabError("limiar invalido: " + repr(value))
    value = int(value)
    if value < 0 or value > MAX_VALUE:
        raise PdiLabError(
            "limiar invalido: "
            + str(value)
            + "; use um inteiro entre 0 e "
            + str(MAX_VALUE)
        )

    return _map_pixels(
        image, lambda pixel: MAX_VALUE if pixel >= value else 0
    )


def histogram(image: np.ndarray) -> list[int]:
    """Conta quantos pixels possuem cada intensidade.

    Devolve uma lista de 256 posições, contada com percurso explícito. A soma
    das contagens é sempre igual ao total de pixels da imagem.
    """
    gray = to_grayscale(image)
    counts = [0] * HISTOGRAM_SIZE

    height, width = gray.shape[0], gray.shape[1]
    for y in range(height):
        row = gray[y].tolist()
        for x in range(width):
            counts[row[x]] += 1

    return counts


def format_histogram(counts: list[int]) -> str:
    """Formata o histograma como CSV no formato definido pelo contrato.

    Gera o cabeçalho ``intensity,count`` seguido de 256 linhas de dados.
    """
    if len(counts) != HISTOGRAM_SIZE:
        raise PdiLabError(
            "histograma deve ter " + str(HISTOGRAM_SIZE) + " posicoes"
        )

    lines = ["intensity,count"]
    for intensity in range(HISTOGRAM_SIZE):
        lines.append(str(intensity) + "," + str(counts[intensity]))
    return "\n".join(lines)


def histogram_summary(counts: list[int]) -> dict:
    """Estatísticas derivadas do histograma, usadas na análise do relatório."""
    total = sum(counts)
    if total == 0:
        raise PdiLabError("histograma vazio")

    weighted = sum(intensity * count for intensity, count in enumerate(counts))
    mean = weighted / total
    variance = sum(
        count * (intensity - mean) ** 2 for intensity, count in enumerate(counts)
    ) / total

    occupied = [intensity for intensity, count in enumerate(counts) if count]

    return {
        "pixels": total,
        "mean": mean,
        "stddev": math.sqrt(variance),
        "min": occupied[0],
        "max": occupied[-1],
        "levels_used": len(occupied),
        "at_zero": counts[0],
        "at_max": counts[MAX_VALUE],
    }
