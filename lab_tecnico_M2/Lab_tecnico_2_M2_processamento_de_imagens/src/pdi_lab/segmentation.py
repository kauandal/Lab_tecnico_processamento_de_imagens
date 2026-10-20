"""Geração, validação e visualização de máscaras binárias.

Convenção da máscara: 255 marca o objeto de interesse e 0 marca o fundo.
Todas as funções devolvem matrizes ``uint8`` de um canal com o mesmo tamanho
da imagem de entrada.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import cv2 as cv
import numpy as np

from .errors import PdiLabError

METHOD_FIXED = "fixed"
METHOD_OTSU = "otsu"
METHOD_ADAPTIVE = "adaptive"
METHOD_HSV = "hsv"
METHODS = (METHOD_FIXED, METHOD_OTSU, METHOD_ADAPTIVE, METHOD_HSV)

ADAPTIVE_MEAN = "mean"
ADAPTIVE_GAUSSIAN = "gaussian"
ADAPTIVE_KINDS = (ADAPTIVE_MEAN, ADAPTIVE_GAUSSIAN)

# Intervalos do OpenCV para imagens de 8 bits: o matiz vai de 0 a 179 (graus
# divididos por 2), saturação e valor vão de 0 a 255.
HUE_MAX = 179
SV_MAX = 255

FOREGROUND = 255
BACKGROUND = 0

# Cores BGR da sobreposição: preenchimento verde translúcido e contorno vermelho.
OVERLAY_FILL = (0, 255, 0)
OVERLAY_EDGE = (0, 0, 255)
OVERLAY_ALPHA = 0.5


@dataclass
class SegmentationResult:
    """Máscara gerada e os parâmetros efetivamente usados para gerá-la."""

    mask: np.ndarray
    details: dict = field(default_factory=dict)


def to_gray(image: np.ndarray) -> np.ndarray:
    """Converte BGR para cinza; imagens de um canal são devolvidas como estão."""
    if image.ndim == 2:
        return image
    return cv.cvtColor(image, cv.COLOR_BGR2GRAY)


def to_bgr(image: np.ndarray) -> np.ndarray:
    """Converte cinza para BGR; imagens de três canais são copiadas."""
    if image.ndim == 2:
        return cv.cvtColor(image, cv.COLOR_GRAY2BGR)
    return image.copy()


def gaussian_blur(image: np.ndarray, size: int) -> np.ndarray:
    """Suavização gaussiana opcional; ``size`` igual a 0 desliga a etapa."""
    if size == 0:
        return image
    if size < 3 or size % 2 == 0:
        raise PdiLabError(
            "--blur deve ser 0 (desligado) ou inteiro impar >= 3, recebido: "
            + str(size)
        )
    return cv.GaussianBlur(image, (size, size), 0)


def threshold_fixed(gray: np.ndarray, threshold: int) -> np.ndarray:
    """Limiar global fixo: objeto onde o cinza é estritamente maior que o limiar.

    Um pixel exatamente igual ao limiar vai para o fundo, que é o
    comportamento de ``cv.THRESH_BINARY``.
    """
    if not 0 <= threshold <= 255:
        raise PdiLabError(
            "--threshold deve estar entre 0 e 255, recebido: " + str(threshold)
        )
    _, mask = cv.threshold(gray, threshold, FOREGROUND, cv.THRESH_BINARY)
    return mask


def threshold_otsu(gray: np.ndarray) -> tuple[np.ndarray, int]:
    """Limiar global escolhido por Otsu; devolve a máscara e o limiar calculado."""
    chosen, mask = cv.threshold(
        gray, 0, FOREGROUND, cv.THRESH_BINARY + cv.THRESH_OTSU
    )
    return mask, int(chosen)


def threshold_adaptive(
    gray: np.ndarray, block_size: int, c: float, kind: str
) -> np.ndarray:
    """Limiar local: objeto onde o pixel supera a média da vizinhança menos ``c``."""
    if block_size < 3 or block_size % 2 == 0:
        raise PdiLabError(
            "--block-size deve ser inteiro impar >= 3, recebido: " + str(block_size)
        )
    if kind not in ADAPTIVE_KINDS:
        raise PdiLabError("--adaptive-kind desconhecido: " + str(kind))

    method = (
        cv.ADAPTIVE_THRESH_MEAN_C
        if kind == ADAPTIVE_MEAN
        else cv.ADAPTIVE_THRESH_GAUSSIAN_C
    )
    return cv.adaptiveThreshold(
        gray, FOREGROUND, method, cv.THRESH_BINARY, block_size, c
    )


def parse_hsv(text: str, name: str) -> tuple[int, int, int]:
    """Lê um triplo ``H,S,V`` e valida os intervalos do OpenCV."""
    parts = [part.strip() for part in str(text).split(",")]
    if len(parts) != 3:
        raise PdiLabError(name + " deve ter o formato H,S,V, recebido: " + str(text))
    try:
        h, s, v = (int(part) for part in parts)
    except ValueError:
        raise PdiLabError(
            name + " deve conter tres inteiros, recebido: " + str(text)
        ) from None

    if not 0 <= h <= HUE_MAX:
        raise PdiLabError(name + ": H deve estar entre 0 e 179, recebido: " + str(h))
    if not 0 <= s <= SV_MAX or not 0 <= v <= SV_MAX:
        raise PdiLabError(
            name + ": S e V devem estar entre 0 e 255, recebido: " + str(text)
        )
    return h, s, v


def hsv_range(
    bgr: np.ndarray, lower: tuple[int, int, int], upper: tuple[int, int, int]
) -> tuple[np.ndarray, bool]:
    """Seleciona pixels dentro do intervalo HSV.

    Quando o matiz inferior é maior que o superior, a faixa cruza a
    descontinuidade 179/0 e é tratada como a união de ``[H_inf, 179]`` e
    ``[0, H_sup]``. Devolve a máscara e se houve essa divisão.
    """
    if bgr.ndim != 3:
        raise PdiLabError(
            "o metodo hsv exige imagem colorida de 3 canais; a entrada tem 1 canal"
        )
    if lower[1] > upper[1] or lower[2] > upper[2]:
        raise PdiLabError(
            "--hsv-lower deve ter S e V menores ou iguais aos de --hsv-upper"
        )

    hsv = cv.cvtColor(bgr, cv.COLOR_BGR2HSV)
    if lower[0] <= upper[0]:
        return cv.inRange(hsv, np.array(lower), np.array(upper)), False

    high = cv.inRange(
        hsv, np.array(lower), np.array((HUE_MAX, upper[1], upper[2]))
    )
    low = cv.inRange(hsv, np.array((0, lower[1], lower[2])), np.array(upper))
    return cv.bitwise_or(high, low), True


def invert_mask(mask: np.ndarray) -> np.ndarray:
    """Troca objeto e fundo, usado quando o objeto é mais escuro que o fundo."""
    return cv.bitwise_not(mask)


def segment(
    image: np.ndarray,
    method: str,
    *,
    threshold: int | None = None,
    block_size: int = 31,
    c: float | None = None,
    adaptive_kind: str = ADAPTIVE_GAUSSIAN,
    hsv_lower: tuple[int, int, int] | None = None,
    hsv_upper: tuple[int, int, int] | None = None,
    blur: int = 0,
    invert: bool = False,
) -> SegmentationResult:
    """Executa o pipeline completo: suavização opcional, método e inversão."""
    if method not in METHODS:
        raise PdiLabError("metodo desconhecido: " + str(method))

    prepared = gaussian_blur(image, blur)
    details: dict = {"method": method, "blur": blur, "invert": invert}

    if method == METHOD_FIXED:
        if threshold is None:
            raise PdiLabError("o metodo fixed exige --threshold")
        mask = threshold_fixed(to_gray(prepared), threshold)
        details["threshold"] = threshold
    elif method == METHOD_OTSU:
        mask, chosen = threshold_otsu(to_gray(prepared))
        details["otsu_threshold"] = chosen
    elif method == METHOD_ADAPTIVE:
        if c is None:
            raise PdiLabError(
                "o metodo adaptive exige --c; use C negativo para objeto claro "
                "e C positivo com --invert para objeto escuro"
            )
        mask = threshold_adaptive(to_gray(prepared), block_size, c, adaptive_kind)
        details.update(
            {"adaptive_kind": adaptive_kind, "block_size": block_size, "c": c}
        )
    else:
        if hsv_lower is None or hsv_upper is None:
            raise PdiLabError("o metodo hsv exige --hsv-lower e --hsv-upper")
        mask, wrapped = hsv_range(prepared, hsv_lower, hsv_upper)
        details.update(
            {
                "hsv_lower": list(hsv_lower),
                "hsv_upper": list(hsv_upper),
                "hue_wraparound": wrapped,
            }
        )

    if invert:
        mask = invert_mask(mask)

    return SegmentationResult(mask=mask, details=details)


def validate_mask(mask: np.ndarray, expected_shape: tuple[int, int]) -> None:
    """Confirma dimensões, canal único, tipo ``uint8`` e valores em {0, 255}."""
    if mask.ndim != 2:
        raise PdiLabError(
            "mascara invalida: esperado 1 canal, obtido shape " + str(mask.shape)
        )
    if mask.shape != tuple(expected_shape):
        raise PdiLabError(
            "mascara invalida: dimensoes "
            + str(mask.shape)
            + " diferentes da entrada "
            + str(tuple(expected_shape))
        )
    if mask.dtype != np.uint8:
        raise PdiLabError("mascara invalida: tipo " + str(mask.dtype) + ", esperado uint8")

    values = set(np.unique(mask).tolist())
    if not values <= {BACKGROUND, FOREGROUND}:
        raise PdiLabError(
            "mascara invalida: valores fora de {0, 255}: "
            + str(sorted(values - {BACKGROUND, FOREGROUND})[:10])
        )


def mask_stats(mask: np.ndarray) -> dict:
    """Contagem e proporção de pixels de primeiro plano."""
    total = int(mask.size)
    foreground = int(np.count_nonzero(mask == FOREGROUND))
    return {
        "pixels": total,
        "foreground": foreground,
        "background": total - foreground,
        "foreground_ratio": foreground / total if total else 0.0,
    }


def overlay(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Imagem original com o objeto tingido de verde e o contorno em vermelho.

    O preenchimento mostra onde a máscara marcou objeto; o contorno facilita
    localizar falsos positivos e falsos negativos nas bordas.
    """
    base = to_bgr(image)
    selected = mask == FOREGROUND
    fill = np.zeros_like(base)
    fill[:] = OVERLAY_FILL

    blended = cv.addWeighted(base, 1.0 - OVERLAY_ALPHA, fill, OVERLAY_ALPHA, 0)
    result = base.copy()
    result[selected] = blended[selected]

    contours, _ = cv.findContours(mask, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)
    cv.drawContours(result, contours, -1, OVERLAY_EDGE, 1)
    return result
