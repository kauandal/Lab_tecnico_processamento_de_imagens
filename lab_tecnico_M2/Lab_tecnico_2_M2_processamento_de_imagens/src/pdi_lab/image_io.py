"""Leitura e escrita de imagens."""

from __future__ import annotations

from pathlib import Path

import cv2 as cv
import numpy as np

from .errors import PdiLabError

# Formatos sem perdas aceitos para gravar máscaras. JPEG fica de fora porque a
# compressão cria valores intermediários e a máscara deixa de ser binária.
LOSSLESS_SUFFIXES = (".png", ".bmp", ".tif", ".tiff")


def load_image(path: str | Path) -> np.ndarray:
    """Carrega uma imagem preservando o número original de canais.

    Levanta ``PdiLabError`` quando o arquivo não existe ou não pode ser
    decodificado, em vez de devolver ``None`` como o OpenCV faz.
    """
    path = Path(path)

    if not path.exists():
        raise PdiLabError(f"arquivo de entrada nao encontrado: {path}")
    if not path.is_file():
        raise PdiLabError(f"caminho de entrada nao e um arquivo: {path}")

    image = cv.imread(str(path), cv.IMREAD_UNCHANGED)
    if image is None:
        raise PdiLabError(f"falha ao decodificar a imagem: {path}")

    if image.dtype != np.uint8:
        raise PdiLabError(
            f"tipo de imagem nao suportado: {image.dtype}; esperado uint8 de 8 bits"
        )
    if image.ndim == 3 and image.shape[2] == 4:
        raise PdiLabError(
            "imagem com 4 canais (BGRA) nao suportada; converta para 3 canais antes"
        )
    if image.ndim not in (2, 3):
        raise PdiLabError(f"formato de imagem inesperado com {image.ndim} dimensoes")

    return image


def save_image(path: str | Path, image: np.ndarray) -> Path:
    """Grava a imagem no caminho indicado, criando o diretório pai se preciso.

    Qualquer falha de gravação, inclusive de pasta ou de formato, vira
    ``PdiLabError`` com mensagem clara, em vez de um traceback.
    """
    path = Path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        written = cv.imwrite(str(path), image)
    except (OSError, cv.error) as error:
        raise PdiLabError(f"falha ao gravar a imagem {path}: {error}") from None

    if not written:
        raise PdiLabError(f"falha ao gravar a imagem: {path}")

    return path


def require_lossless(path: str | Path) -> None:
    """Recusa extensões com perdas para arquivos que precisam ficar binários."""
    suffix = Path(path).suffix.lower()
    if suffix not in LOSSLESS_SUFFIXES:
        raise PdiLabError(
            "formato de saida nao aceito para mascara: '"
            + suffix
            + "'; use "
            + ", ".join(LOSSLESS_SUFFIXES)
        )


def channel_count(image: np.ndarray) -> int:
    """Número de canais da imagem: 1 para escala de cinza, 3 para BGR."""
    return 1 if image.ndim == 2 else image.shape[2]
