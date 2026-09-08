"""Operações do laboratório M1.1 implementadas manualmente.

Todas as operações avaliadas percorrem os pixels explicitamente. Nenhuma função
pronta de cópia, separação de canais, conversão para níveis de cinza ou
quantização é utilizada.

Notas numéricas
---------------
Cada linha é convertida para lista Python com ``tolist()`` antes do percurso.
Isso mantém o acesso pixel a pixel e faz as contas com inteiros de precisão
arbitrária do Python, eliminando o estouro que ocorre ao somar três ``uint8``
diretamente. A saturação e o arredondamento acontecem apenas no momento de
gravar o valor final no resultado.
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

CHANNEL_INDEX = {"b": 0, "g": 1, "r": 2}

MAX_VALUE = 255
MIN_LEVELS = 2
MAX_LEVELS = 256


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


def require_color(image: np.ndarray, operation: str) -> None:
    """Garante que a operação recebeu uma imagem BGR de 3 canais."""
    channels = channel_count(image)
    if channels != 3:
        raise PdiLabError(
            "a operacao "
            + operation
            + " exige imagem colorida de 3 canais; a entrada possui "
            + str(channels)
        )


def inspect_image(image: np.ndarray) -> dict:
    """Coleta as estatísticas pedidas no enunciado com percurso manual.

    Devolve dimensões, canais, tipo, total de pixels e mínimo, máximo e média
    das intensidades. Para imagens coloridas, também por canal.
    """
    height, width = image.shape[0], image.shape[1]
    channels = channel_count(image)
    total_pixels = height * width

    minimums = [MAX_VALUE] * channels
    maximums = [0] * channels
    sums = [0] * channels

    for y in range(height):
        row = image[y].tolist()
        for x in range(width):
            pixel = row[x] if channels > 1 else [row[x]]
            for c in range(channels):
                value = pixel[c]
                sums[c] += value
                if value < minimums[c]:
                    minimums[c] = value
                if value > maximums[c]:
                    maximums[c] = value

    means = [total / total_pixels for total in sums]

    stats = {
        "width": width,
        "height": height,
        "channels": channels,
        "pixels": total_pixels,
        "type": str(image.dtype),
        "min": min(minimums),
        "max": max(maximums),
        "mean": sum(sums) / (total_pixels * channels),
    }

    if channels == 3:
        for name, index in CHANNEL_INDEX.items():
            stats["min_" + name] = minimums[index]
            stats["max_" + name] = maximums[index]
            stats["mean_" + name] = means[index]

    return stats


def format_inspection(stats: dict) -> str:
    """Formata as estatísticas como pares chave=valor, uma por linha."""
    lines = []
    for key, value in stats.items():
        if isinstance(value, float):
            lines.append("{0}={1:.4f}".format(key, value))
        else:
            lines.append("{0}={1}".format(key, value))
    return "\n".join(lines)


def copy_image(image: np.ndarray) -> np.ndarray:
    """Copia a imagem pixel a pixel para uma nova matriz.

    O resultado é numericamente idêntico à entrada.
    """
    height, width = image.shape[0], image.shape[1]
    channels = channel_count(image)

    if channels == 1:
        result = np.zeros((height, width), dtype=np.uint8)
    else:
        result = np.zeros((height, width, channels), dtype=np.uint8)

    for y in range(height):
        source_row = image[y].tolist()
        target_row = [0] * width
        for x in range(width):
            target_row[x] = source_row[x]
        result[y] = target_row

    return result


def extract_channel(image: np.ndarray, channel: str) -> np.ndarray:
    """Isola um canal preservando seu valor e zerando os demais.

    O parâmetro ``channel`` aceita ``b``, ``g`` ou ``r``. A saída continua com
    3 canais para que a cor do canal isolado permaneça visível.
    """
    key = channel.lower()
    if key not in CHANNEL_INDEX:
        raise PdiLabError(
            "canal invalido: " + str(channel) + "; use um entre b, g ou r"
        )
    require_color(image, "channel_" + key)

    index = CHANNEL_INDEX[key]
    height, width = image.shape[0], image.shape[1]
    result = np.zeros((height, width, 3), dtype=np.uint8)

    for y in range(height):
        source_row = image[y].tolist()
        target_row = [None] * width
        for x in range(width):
            pixel = [0, 0, 0]
            pixel[index] = source_row[x][index]
            target_row[x] = pixel
        result[y] = target_row

    return result


def grayscale_average(image: np.ndarray) -> np.ndarray:
    """Converte para níveis de cinza pela média simples ``(R + G + B) / 3``.

    A soma é feita com inteiros Python, portanto não estoura em pixels claros.
    """
    require_color(image, "grayscale_average")

    height, width = image.shape[0], image.shape[1]
    result = np.zeros((height, width), dtype=np.uint8)

    for y in range(height):
        source_row = image[y].tolist()
        target_row = [0] * width
        for x in range(width):
            blue, green, red = source_row[x]
            target_row[x] = _clamp_to_uint8((blue + green + red) / 3.0)
        result[y] = target_row

    return result


def grayscale_weighted(image: np.ndarray) -> np.ndarray:
    """Converte para níveis de cinza pela média ponderada da luminância.

    Aplica ``g = 0,299R + 0,587G + 0,114B`` acumulando em ponto flutuante.
    """
    require_color(image, "grayscale_weighted")

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


def quantize(image: np.ndarray, levels: int) -> np.ndarray:
    """Reduz a resolução radiométrica da imagem para ``levels`` níveis.

    Espera uma imagem em níveis de cinza. Se receber uma imagem colorida, a
    conversão ponderada é aplicada antes, porque o enunciado parte de uma
    imagem em níveis de cinza.

    Os níveis resultantes ficam distribuídos uniformemente entre 0 e 255, de
    forma que o menor nível seja 0 e o maior seja 255.
    """
    if isinstance(levels, bool) or not isinstance(levels, (int, np.integer)):
        raise PdiLabError("quantidade de niveis invalida: " + repr(levels))
    levels = int(levels)
    if levels < MIN_LEVELS or levels > MAX_LEVELS:
        raise PdiLabError(
            "quantidade de niveis invalida: "
            + str(levels)
            + "; use um inteiro entre "
            + str(MIN_LEVELS)
            + " e "
            + str(MAX_LEVELS)
        )

    if channel_count(image) == 3:
        image = grayscale_weighted(image)

    step = MAX_VALUE / (levels - 1)
    height, width = image.shape[0], image.shape[1]
    result = np.zeros((height, width), dtype=np.uint8)

    for y in range(height):
        source_row = image[y].tolist()
        target_row = [0] * width
        for x in range(width):
            index = _round_half_up(source_row[x] / step)
            if index < 0:
                index = 0
            elif index > levels - 1:
                index = levels - 1
            target_row[x] = _clamp_to_uint8(index * step)
        result[y] = target_row

    return result
