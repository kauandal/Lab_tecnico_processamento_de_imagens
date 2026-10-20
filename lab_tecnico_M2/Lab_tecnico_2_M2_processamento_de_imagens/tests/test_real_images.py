"""Processa as duas imagens reais do estudo pelas configurações comparadas."""

from pathlib import Path

import cv2 as cv
import numpy as np
import pytest

from pdi_lab.cli import main

INPUT = Path(__file__).resolve().parent.parent / "images" / "input"

# Mesmos parâmetros do lab_1_m2.py.
CONFIGS = {
    ("coins.png", "fixed"): ["--method", "fixed", "--threshold", "120"],
    ("coins.png", "otsu"): ["--method", "otsu"],
    ("moedas_real_separadas.jpg", "fixed"): ["--method", "fixed", "--threshold", "85", "--invert"],
    ("moedas_real_separadas.jpg", "otsu"): ["--method", "otsu", "--invert"],
    ("moedas_real_separadas.jpg", "hsv"): [
        "--method", "hsv", "--hsv-lower", "0,30,0", "--hsv-upper", "179,255,255", "--blur", "5",
    ],
}


def segment(name, config, output):
    code = main(
        [
            "--input",
            str(INPUT / name),
            "--output",
            str(output),
            "--operation",
            "segment",
            *CONFIGS[(name, config)],
        ]
    )
    assert code == 0
    return cv.imread(str(output), cv.IMREAD_UNCHANGED)


@pytest.mark.parametrize("name, config", list(CONFIGS), ids=lambda value: str(value))
def test_mascara_real_valida(tmp_path, name, config):
    image = cv.imread(str(INPUT / name), cv.IMREAD_UNCHANGED)
    mask = segment(name, config, tmp_path / "mask.png")

    assert mask.ndim == 2
    assert mask.shape == image.shape[:2]
    assert set(np.unique(mask).tolist()) <= {0, 255}
    assert 0 < np.count_nonzero(mask) < mask.size


def test_coins_limiar_fixo_marca_o_fundo_claro_do_topo(tmp_path):
    """Limitação: o topo da imagem é só fundo, mas é claro e entra como moeda."""
    mask = segment("coins.png", "fixed", tmp_path / "mask.png")

    topo = mask[:25]
    assert np.count_nonzero(topo) / topo.size > 0.2


def test_separadas_limiar_fixo_marca_o_canto_escuro(tmp_path):
    """Limitação: o canto inferior esquerdo é só fundo, mas é escuro e entra como moeda.

    O HSV usa a saturação, que quase não muda com o escurecimento do canto.
    """
    name = "moedas_real_separadas.jpg"
    fixed = segment(name, "fixed", tmp_path / "fixed.png")
    hsv = segment(name, "hsv", tmp_path / "hsv.png")

    canto_fixed = fixed[-300:, :300]
    canto_hsv = hsv[-300:, :300]
    assert np.count_nonzero(canto_fixed) / canto_fixed.size > 0.5
    assert np.count_nonzero(canto_hsv) / canto_hsv.size < 0.05
