"""Testes das funções de segmentação com imagens sintéticas de resultado previsível."""

import cv2 as cv
import numpy as np
import pytest

from pdi_lab import segmentation as seg
from pdi_lab.errors import PdiLabError


def hsv_pixels(*hues):
    """Imagem BGR de uma linha com cores puras nos matizes informados."""
    hsv = np.array([[(h, 255, 255) for h in hues]], dtype=np.uint8)
    return cv.cvtColor(hsv, cv.COLOR_HSV2BGR)


# --- limiar fixo ---------------------------------------------------------


def test_limiar_fixo_no_limiar_e_dos_dois_lados():
    """Valor igual ao limiar vai para o fundo; só valores maiores viram objeto."""
    gray = np.array([[0, 119, 120, 121, 255]], dtype=np.uint8)

    mask = seg.threshold_fixed(gray, 120)

    assert mask.tolist() == [[0, 0, 0, 255, 255]]


def test_limiar_fixo_extremos():
    gray = np.array([[0, 1, 254, 255]], dtype=np.uint8)

    assert seg.threshold_fixed(gray, 0).tolist() == [[0, 255, 255, 255]]
    assert seg.threshold_fixed(gray, 255).tolist() == [[0, 0, 0, 0]]


def test_inversao_para_objeto_escuro():
    gray = np.array([[0, 119, 120, 121, 255]], dtype=np.uint8)

    mask, info = seg.segment(gray, "fixed", threshold=120, invert=True)

    assert mask.tolist() == [[255, 255, 255, 0, 0]]
    assert info["invert"] is True


@pytest.mark.parametrize("threshold", [-1, 256])
def test_limiar_fora_do_intervalo(threshold):
    gray = np.zeros((2, 2), dtype=np.uint8)

    with pytest.raises(PdiLabError):
        seg.threshold_fixed(gray, threshold)


def test_fixed_sem_limiar():
    with pytest.raises(PdiLabError):
        seg.segment(np.zeros((2, 2), dtype=np.uint8), "fixed")


def test_limiar_fixo_em_imagem_colorida_usa_cinza():
    bgr = np.zeros((2, 2, 3), dtype=np.uint8)
    bgr[0, 0] = (255, 255, 255)

    mask, _ = seg.segment(bgr, "fixed", threshold=128)

    assert mask.shape == (2, 2)
    assert mask.tolist() == [[255, 0], [0, 0]]


# --- Otsu ----------------------------------------------------------------


def test_otsu_separa_imagem_bimodal():
    gray = np.full((10, 10), 50, dtype=np.uint8)
    gray[:, 5:] = 200

    mask, chosen = seg.threshold_otsu(gray)

    assert 50 <= chosen < 200
    assert np.all(mask[:, 5:] == 255)
    assert np.all(mask[:, :5] == 0)


# --- adaptativo ----------------------------------------------------------


def test_adaptativo_com_c_negativo_marca_objeto_claro():
    gray = np.full((31, 31), 20, dtype=np.uint8)
    gray[12:19, 12:19] = 200

    mask = seg.threshold_adaptive(gray, 31, -5.0, "mean")

    assert mask[15, 15] == 255
    assert mask[0, 0] == 0


def test_adaptativo_em_regiao_plana_depende_do_sinal_de_c():
    """Região plana: com C positivo vira objeto, com C negativo vira fundo."""
    flat = np.full((15, 15), 100, dtype=np.uint8)

    assert np.all(seg.threshold_adaptive(flat, 5, 5.0, "mean") == 255)
    assert np.all(seg.threshold_adaptive(flat, 5, -5.0, "mean") == 0)


@pytest.mark.parametrize("block_size", [1, 2, 4])
def test_adaptativo_bloco_invalido(block_size):
    with pytest.raises(PdiLabError):
        seg.threshold_adaptive(np.zeros((5, 5), dtype=np.uint8), block_size, 0, "mean")


def test_adaptativo_sem_c():
    with pytest.raises(PdiLabError):
        seg.segment(np.zeros((5, 5), dtype=np.uint8), "adaptive")


# --- HSV -----------------------------------------------------------------


def test_hsv_intervalo_simples():
    bgr = hsv_pixels(0, 60, 120)

    mask, wrapped = seg.hsv_range(bgr, (50, 100, 100), (70, 255, 255))

    assert wrapped is False
    assert mask.tolist() == [[0, 255, 0]]


def test_hsv_faixa_que_cruza_179_e_0():
    """Vermelho fica dos dois lados da descontinuidade do matiz."""
    bgr = hsv_pixels(175, 5, 60, 120)

    mask, wrapped = seg.hsv_range(bgr, (170, 100, 100), (10, 255, 255))

    assert wrapped is True
    assert mask.tolist() == [[255, 255, 0, 0]]


def test_hsv_exige_imagem_colorida():
    with pytest.raises(PdiLabError):
        seg.hsv_range(np.zeros((2, 2), dtype=np.uint8), (0, 0, 0), (10, 255, 255))


def test_hsv_limites_s_v_invertidos():
    with pytest.raises(PdiLabError):
        seg.hsv_range(hsv_pixels(0), (0, 200, 0), (10, 100, 255))


@pytest.mark.parametrize("text", ["180,0,0", "0,256,0", "1,2", "a,b,c", "-1,0,0"])
def test_parse_hsv_invalido(text):
    with pytest.raises(PdiLabError):
        seg.parse_hsv(text, "--hsv-lower")


def test_parse_hsv_valido():
    assert seg.parse_hsv(" 170, 80 ,50", "--hsv-lower") == (170, 80, 50)


# --- pré-processamento e método -----------------------------------------


def test_blur_zero_nao_altera():
    image = np.arange(25, dtype=np.uint8).reshape(5, 5)

    assert seg.gaussian_blur(image, 0) is image


@pytest.mark.parametrize("size", [1, 2, 4, -3])
def test_blur_invalido(size):
    with pytest.raises(PdiLabError):
        seg.gaussian_blur(np.zeros((5, 5), dtype=np.uint8), size)


def test_metodo_desconhecido():
    with pytest.raises(PdiLabError):
        seg.segment(np.zeros((2, 2), dtype=np.uint8), "kmeans")


# --- validação, estatísticas e sobreposição ------------------------------


def test_validacao_aceita_mascara_binaria():
    mask = np.array([[0, 255], [255, 0]], dtype=np.uint8)

    seg.validate_mask(mask, (2, 2))


@pytest.mark.parametrize(
    "mask, shape",
    [
        (np.array([[0, 128]], dtype=np.uint8), (1, 2)),
        (np.zeros((2, 2, 3), dtype=np.uint8), (2, 2)),
        (np.zeros((2, 3), dtype=np.uint8), (2, 2)),
        (np.zeros((2, 2), dtype=np.uint16), (2, 2)),
    ],
    ids=["valor_intermediario", "tres_canais", "dimensao_diferente", "tipo_16_bits"],
)
def test_validacao_recusa_mascara_invalida(mask, shape):
    with pytest.raises(PdiLabError):
        seg.validate_mask(mask, shape)


def test_estatisticas_de_primeiro_plano():
    mask = np.zeros((4, 5), dtype=np.uint8)
    mask[0, :] = 255

    stats = seg.mask_stats(mask)

    assert stats["pixels"] == 20
    assert stats["foreground"] == 5
    assert stats["background"] == 15
    assert stats["foreground_ratio"] == pytest.approx(0.25)


def test_sobreposicao_preserva_o_fundo():
    image = np.full((9, 9), 80, dtype=np.uint8)
    mask = np.zeros((9, 9), dtype=np.uint8)
    mask[3:6, 3:6] = 255

    result = seg.overlay(image, mask)

    assert result.shape == (9, 9, 3)
    assert np.all(result[mask == 0] == 80)
    assert not np.array_equal(result[4, 4], np.array([80, 80, 80]))
