"""Segmentacao do M2.1. A mascara usa 255 para a moeda e 0 para o fundo."""

import cv2 as cv
import numpy as np

from .errors import PdiLabError

METHODS = ["fixed", "otsu", "adaptive", "hsv"]
ADAPTIVE_KINDS = ["mean", "gaussian"]


def to_gray(image):
    if len(image.shape) == 2:
        return image
    return cv.cvtColor(image, cv.COLOR_BGR2GRAY)


def to_bgr(image):
    if len(image.shape) == 2:
        return cv.cvtColor(image, cv.COLOR_GRAY2BGR)
    return image.copy()


def gaussian_blur(image, size):
    # 0 desliga a suavizacao
    if size == 0:
        return image
    if size < 3 or size % 2 == 0:
        raise PdiLabError("--blur deve ser 0 (desligado) ou inteiro impar >= 3, recebido: " + str(size))
    return cv.GaussianBlur(image, (size, size), 0)


def threshold_fixed(gray, threshold):
    # moeda onde o cinza e maior que o limiar; igual ao limiar vai para o fundo
    if threshold < 0 or threshold > 255:
        raise PdiLabError("--threshold deve estar entre 0 e 255, recebido: " + str(threshold))
    _, mask = cv.threshold(gray, threshold, 255, cv.THRESH_BINARY)
    return mask


def threshold_otsu(gray):
    t, mask = cv.threshold(gray, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    return mask, int(t)


def threshold_adaptive(gray, block_size, c, kind):
    # moeda onde o pixel e maior que a media local - c
    if block_size < 3 or block_size % 2 == 0:
        raise PdiLabError("--block-size deve ser inteiro impar >= 3, recebido: " + str(block_size))
    if kind == "mean":
        method = cv.ADAPTIVE_THRESH_MEAN_C
    elif kind == "gaussian":
        method = cv.ADAPTIVE_THRESH_GAUSSIAN_C
    else:
        raise PdiLabError("--adaptive-kind desconhecido: " + str(kind))
    return cv.adaptiveThreshold(gray, 255, method, cv.THRESH_BINARY, block_size, c)


def parse_hsv(text, name):
    # le "H,S,V" e confere os intervalos do OpenCV (H vai de 0 a 179)
    parts = str(text).split(",")
    if len(parts) != 3:
        raise PdiLabError(name + " deve ter o formato H,S,V, recebido: " + str(text))
    try:
        h = int(parts[0])
        s = int(parts[1])
        v = int(parts[2])
    except ValueError:
        raise PdiLabError(name + " deve conter tres inteiros, recebido: " + str(text))

    if h < 0 or h > 179:
        raise PdiLabError(name + ": H deve estar entre 0 e 179, recebido: " + str(h))
    if s < 0 or s > 255 or v < 0 or v > 255:
        raise PdiLabError(name + ": S e V devem estar entre 0 e 255, recebido: " + str(text))
    return (h, s, v)


def hsv_range(image, lower, upper):
    if len(image.shape) != 3:
        raise PdiLabError("o metodo hsv exige imagem colorida de 3 canais; a entrada tem 1 canal")
    if lower[1] > upper[1] or lower[2] > upper[2]:
        raise PdiLabError("--hsv-lower deve ter S e V menores ou iguais aos de --hsv-upper")

    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    if lower[0] <= upper[0]:
        mask = cv.inRange(hsv, np.array(lower), np.array(upper))
        return mask, False

    # H inferior maior que o superior: a faixa passa pelo 179 e volta ao 0,
    # entao junta as duas partes
    part1 = cv.inRange(hsv, np.array(lower), np.array([179, upper[1], upper[2]]))
    part2 = cv.inRange(hsv, np.array([0, lower[1], lower[2]]), np.array(upper))
    return cv.bitwise_or(part1, part2), True


def segment(image, method, threshold=None, block_size=31, c=None, adaptive_kind="gaussian",
            hsv_lower=None, hsv_upper=None, blur=0, invert=False):
    """Suavizacao opcional, metodo e inversao. Devolve a mascara e os parametros usados."""
    if method not in METHODS:
        raise PdiLabError("metodo desconhecido: " + str(method))

    image = gaussian_blur(image, blur)
    info = {"method": method, "blur": blur, "invert": invert}

    if method == "fixed":
        if threshold is None:
            raise PdiLabError("o metodo fixed exige --threshold")
        mask = threshold_fixed(to_gray(image), threshold)
        info["threshold"] = threshold
    elif method == "otsu":
        mask, t = threshold_otsu(to_gray(image))
        info["otsu_threshold"] = t
    elif method == "adaptive":
        if c is None:
            raise PdiLabError("o metodo adaptive exige --c; use C negativo para objeto claro "
                              "e C positivo com --invert para objeto escuro")
        mask = threshold_adaptive(to_gray(image), block_size, c, adaptive_kind)
        info["adaptive_kind"] = adaptive_kind
        info["block_size"] = block_size
        info["c"] = c
    else:
        if hsv_lower is None or hsv_upper is None:
            raise PdiLabError("o metodo hsv exige --hsv-lower e --hsv-upper")
        mask, wrapped = hsv_range(image, hsv_lower, hsv_upper)
        info["hsv_lower"] = list(hsv_lower)
        info["hsv_upper"] = list(hsv_upper)
        info["hue_wraparound"] = wrapped

    # para moeda mais escura que o fundo
    if invert:
        mask = cv.bitwise_not(mask)

    return mask, info


def validate_mask(mask, shape):
    # confere o que o enunciado pede: 1 canal, mesmo tamanho, uint8, so 0 e 255
    if len(mask.shape) != 2:
        raise PdiLabError("mascara invalida: esperado 1 canal, obtido shape " + str(mask.shape))
    if mask.shape != tuple(shape):
        raise PdiLabError("mascara invalida: dimensoes " + str(mask.shape)
                          + " diferentes da entrada " + str(tuple(shape)))
    if mask.dtype != np.uint8:
        raise PdiLabError("mascara invalida: tipo " + str(mask.dtype) + ", esperado uint8")
    values = set(np.unique(mask).tolist())
    if not values <= {0, 255}:
        others = sorted(values - {0, 255})
        raise PdiLabError("mascara invalida: valores fora de {0, 255}: " + str(others[:10]))


def mask_stats(mask):
    total = mask.size
    foreground = int(np.count_nonzero(mask == 255))
    return {
        "pixels": int(total),
        "foreground": foreground,
        "background": int(total) - foreground,
        "foreground_ratio": foreground / total if total else 0.0,
    }


def overlay(image, mask):
    """Original com a moeda pintada de verde e o contorno da mascara em vermelho."""
    result = to_bgr(image)
    green = np.zeros_like(result)
    green[:] = (0, 255, 0)
    mixed = cv.addWeighted(result, 0.5, green, 0.5, 0)
    result[mask == 255] = mixed[mask == 255]

    contours, _ = cv.findContours(mask, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)
    cv.drawContours(result, contours, -1, (0, 0, 255), 1)
    return result
