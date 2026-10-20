"""Reexecuta a análise do M2.2 nas máscaras das duas imagens do estudo."""

import csv
import json
from pathlib import Path

import cv2 as cv
import numpy as np
import pytest

from pdi_lab.cli import main

PROJECT = Path(__file__).resolve().parent.parent
INPUT = PROJECT / "images" / "input"
SEQUENCE = PROJECT / "config" / "sequence.json"

# Mesmos parâmetros do M2.1 (lab_1_m2.py) para gerar a máscara de trabalho.
SEGMENT = {
    "coins.png": ["--method", "fixed", "--threshold", "120"],
    "moedas_brasileiras.jpg": ["--method", "fixed", "--threshold", "230", "--invert"],
}


def areas(path):
    with open(path, newline="", encoding="utf-8") as file:
        return [int(row["area"]) for row in csv.DictReader(file)]


@pytest.mark.parametrize("name", list(SEGMENT))
def test_reexecucao_com_saidas_intermediarias(tmp_path, name):
    mask_path = tmp_path / "mask.png"
    prefix = tmp_path / "cena"

    assert (
        main(
            [
                "--input",
                str(INPUT / name),
                "--output",
                str(mask_path),
                "--operation",
                "segment",
                *SEGMENT[name],
            ]
        )
        == 0
    )
    assert (
        main(
            [
                "--input",
                str(mask_path),
                "--output",
                str(prefix),
                "--operation",
                "analyze",
                "--sequence",
                str(SEQUENCE),
                "--min-area",
                "100",
            ]
        )
        == 0
    )

    for suffix in ("_stage_1_open.png", "_stage_2_close.png", "_labels.png"):
        assert Path(str(prefix) + suffix).exists(), suffix

    # Antes de qualquer filtro, a soma das áreas é o total de pixels de objeto.
    initial_mask = cv.imread(str(mask_path), cv.IMREAD_UNCHANGED)
    final_mask = cv.imread(str(prefix) + "_final_mask.png", cv.IMREAD_UNCHANGED)
    assert sum(areas(str(prefix) + "_initial.csv")) == np.count_nonzero(initial_mask)
    assert sum(areas(str(prefix) + "_final.csv")) == np.count_nonzero(final_mask)

    summary = json.loads(Path(str(prefix) + "_summary.json").read_text(encoding="utf-8"))
    assert summary["final"]["count_raw"] < summary["initial"]["count_raw"]


def test_coins_contagem_filtrada_inclui_a_faixa_do_fundo(tmp_path):
    """24 moedas reais, mas a faixa clara do topo continua como um componente."""
    mask_path = tmp_path / "mask.png"
    prefix = tmp_path / "coins"
    main(["--input", str(INPUT / "coins.png"), "--output", str(mask_path),
          "--operation", "segment", *SEGMENT["coins.png"]])
    main(["--input", str(mask_path), "--output", str(prefix), "--operation", "analyze",
          "--sequence", str(SEQUENCE), "--min-area", "100"])

    summary = json.loads(Path(str(prefix) + "_summary.json").read_text(encoding="utf-8"))
    assert summary["final"]["count_kept"] == 25
