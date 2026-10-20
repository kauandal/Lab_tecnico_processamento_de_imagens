"""Processa as duas imagens reais do estudo pelas duas configurações."""

from pathlib import Path

import cv2 as cv
import numpy as np
import pytest

from pdi_lab.cli import main

INPUT = Path(__file__).resolve().parent.parent / "images" / "input"

# Mesmos parâmetros do lab_1_m2.py.
FIXED = {
    "coins.png": ["--method", "fixed", "--threshold", "120"],
    "moedas_brasileiras.jpg": ["--method", "fixed", "--threshold", "230", "--invert"],
}
OTSU = {
    "coins.png": ["--method", "otsu"],
    "moedas_brasileiras.jpg": ["--method", "otsu", "--invert"],
}


def segment(name, method_args, output):
    code = main(
        [
            "--input",
            str(INPUT / name),
            "--output",
            str(output),
            "--operation",
            "segment",
            *method_args,
        ]
    )
    assert code == 0
    return cv.imread(str(output), cv.IMREAD_UNCHANGED)


@pytest.mark.parametrize("config", [FIXED, OTSU], ids=["fixed", "otsu"])
@pytest.mark.parametrize("name", ["coins.png", "moedas_brasileiras.jpg"])
def test_mascara_real_valida(tmp_path, name, config):
    image = cv.imread(str(INPUT / name), cv.IMREAD_UNCHANGED)
    mask = segment(name, config[name], tmp_path / "mask.png")

    assert mask.ndim == 2
    assert mask.shape == image.shape[:2]
    assert set(np.unique(mask).tolist()) <= {0, 255}
    assert 0 < np.count_nonzero(mask) < mask.size


def test_coins_limiar_fixo_marca_o_fundo_claro_do_topo(tmp_path):
    """Limitação: o topo da imagem é só fundo, mas é claro e entra como moeda."""
    mask = segment("coins.png", FIXED["coins.png"], tmp_path / "mask.png")

    topo = mask[:25]
    assert np.count_nonzero(topo) / topo.size > 0.2


def test_moedas_otsu_perde_o_interior_das_moedas(tmp_path):
    """Limitação: com o fundo branco dominando, o Otsu separa tons dentro das moedas."""
    name = "moedas_brasileiras.jpg"
    fixed = segment(name, FIXED[name], tmp_path / "fixed.png")
    otsu = segment(name, OTSU[name], tmp_path / "otsu.png")

    assert np.count_nonzero(otsu) < 0.7 * np.count_nonzero(fixed)
