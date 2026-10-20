"""Reexecuta a análise do M2.2 nas máscaras das imagens do estudo."""

import csv
import json
from pathlib import Path

import cv2 as cv
import numpy as np
import pytest

from pdi_lab.cli import main

PROJECT = Path(__file__).resolve().parent.parent
INPUT = PROJECT / "images" / "input"
CONFIG = PROJECT / "config"

# Mesmos parâmetros do lab_1_m2.py e do lab_2_m2.py.
CASES = {
    "coins.png": {
        "segment": ["--method", "fixed", "--threshold", "120"],
        "sequence": "coins.json",
        "min_area": "500",
    },
    "moedas_real_separadas.jpg": {
        "segment": ["--method", "hsv", "--hsv-lower", "0,30,0", "--hsv-upper", "179,255,255", "--blur", "5"],
        "sequence": "moedas_real.json",
        "min_area": "50000",
    },
    "moedas_real_empilhadas.jpg": {
        "segment": ["--method", "otsu", "--invert", "--blur", "5"],
        "sequence": "moedas_real.json",
        "min_area": "50000",
    },
}


def run_case(tmp_path, name):
    case = CASES[name]
    mask_path = tmp_path / "mask.png"
    prefix = tmp_path / "cena"
    segment = ["--input", str(INPUT / name), "--output", str(mask_path), "--operation", "segment"]
    analyze = [
        "--input", str(mask_path), "--output", str(prefix), "--operation", "analyze",
        "--sequence", str(CONFIG / case["sequence"]), "--min-area", case["min_area"],
    ]
    assert main(segment + case["segment"]) == 0
    assert main(analyze) == 0
    summary = json.loads(Path(str(prefix) + "_summary.json").read_text(encoding="utf-8"))
    return mask_path, prefix, summary


def areas(path):
    with open(path, newline="", encoding="utf-8") as file:
        return [int(row["area"]) for row in csv.DictReader(file)]


@pytest.mark.parametrize("name", list(CASES))
def test_reexecucao_com_saidas_intermediarias(tmp_path, name):
    mask_path, prefix, summary = run_case(tmp_path, name)

    for suffix in ("_stage_1_open.png", "_stage_2_close.png", "_labels.png"):
        assert Path(str(prefix) + suffix).exists(), suffix

    # Antes de qualquer filtro, a soma das áreas é o total de pixels de objeto.
    initial_mask = cv.imread(str(mask_path), cv.IMREAD_UNCHANGED)
    final_mask = cv.imread(str(prefix) + "_final_mask.png", cv.IMREAD_UNCHANGED)
    assert sum(areas(str(prefix) + "_initial.csv")) == np.count_nonzero(initial_mask)
    assert sum(areas(str(prefix) + "_final.csv")) == np.count_nonzero(final_mask)

    assert summary["final"]["count_raw"] < summary["initial"]["count_raw"]


def test_coins_contagem_filtrada_inclui_a_faixa_do_fundo(tmp_path):
    """24 moedas reais, mas a faixa clara do topo continua como um componente."""
    _, _, summary = run_case(tmp_path, "coins.png")

    assert summary["final"]["count_kept"] == 25


def test_separadas_contagem_igual_ao_numero_de_moedas(tmp_path):
    _, _, summary = run_case(tmp_path, "moedas_real_separadas.jpg")

    assert summary["final"]["count_kept"] == 12


def test_empilhadas_contato_junta_moedas_num_componente(tmp_path):
    """Moedas encostadas viram um componente só, e o fechamento junta mais."""
    _, prefix, summary = run_case(tmp_path, "moedas_real_empilhadas.jpg")

    final = areas(str(prefix) + "_final.csv")
    assert summary["final"]["count_kept"] < summary["initial"]["count_kept"]
    assert max(final) > 0.8 * sum(final)
