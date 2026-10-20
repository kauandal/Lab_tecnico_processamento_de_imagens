"""Leitura e escrita de imagens."""

from pathlib import Path

import cv2 as cv
import numpy as np

from .errors import PdiLabError

# formatos sem perdas para a mascara; JPEG cria valores no meio e a mascara
# deixa de ser binaria
LOSSLESS_SUFFIXES = [".png", ".bmp", ".tif", ".tiff"]


def load_image(path):
    path = Path(path)
    if not path.exists():
        raise PdiLabError("arquivo de entrada nao encontrado: " + str(path))
    if not path.is_file():
        raise PdiLabError("caminho de entrada nao e um arquivo: " + str(path))

    # o imread devolve None quando nao consegue ler, entao conferimos aqui
    image = cv.imread(str(path), cv.IMREAD_UNCHANGED)
    if image is None:
        raise PdiLabError("falha ao decodificar a imagem: " + str(path))

    if image.dtype != np.uint8:
        raise PdiLabError("tipo de imagem nao suportado: " + str(image.dtype) + "; esperado uint8 de 8 bits")
    if len(image.shape) == 3 and image.shape[2] == 4:
        raise PdiLabError("imagem com 4 canais (BGRA) nao suportada; converta para 3 canais antes")
    if len(image.shape) not in (2, 3):
        raise PdiLabError("formato de imagem inesperado com " + str(len(image.shape)) + " dimensoes")
    return image


def save_image(path, image):
    path = Path(path)
    # qualquer erro de pasta ou de gravacao vira mensagem clara, sem traceback
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        ok = cv.imwrite(str(path), image)
    except (OSError, cv.error) as error:
        raise PdiLabError("falha ao gravar a imagem " + str(path) + ": " + str(error))
    if not ok:
        raise PdiLabError("falha ao gravar a imagem: " + str(path))
    return path


def require_lossless(path):
    suffix = Path(path).suffix.lower()
    if suffix not in LOSSLESS_SUFFIXES:
        raise PdiLabError("formato de saida nao aceito para mascara: '" + suffix
                          + "'; use " + ", ".join(LOSSLESS_SUFFIXES))
