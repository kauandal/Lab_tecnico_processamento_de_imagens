"""Reproduz todas as saídas do laboratório M2.2 em uma única execução.

Primeiro refaz as máscaras do M2.1 com ``lab_1_m2.py`` e depois executa a
operação ``analyze`` sobre cada máscara escolhida. Cada análise também pode ser
executada isoladamente pela linha de comando::

    python -m pdi_lab --input <mascara.png> --output <prefixo> --operation analyze --sequence <config.json>

Uso::

    python lab_2_m2.py
"""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Os caminhos deste script sao relativos a raiz do projeto, de forma que ele
# funcione a partir de qualquer diretorio de trabalho.
os.chdir(PROJECT_ROOT)

import cv2 as cv  # noqa: E402
import numpy as np  # noqa: E402

import lab_1_m2  # noqa: E402
from pdi_lab.cli import main as pdi_lab  # noqa: E402

OUTPUT_DIR = Path("images/output")
RESULTS_DIR = Path("results")

CONNECTIVITY = 8
MIN_AREA = 100

# Cada análise: máscara do M2.1, prefixo das saídas e sequência morfológica.
# A última é o caso de comparação com fechamento exagerado.
ANALYSES = [
    {"mask": "coins_mask.png", "prefix": "coins", "sequence": "config/sequence.json"},
    {
        "mask": "moedas_brasileiras_mask.png",
        "prefix": "moedas_brasileiras",
        "sequence": "config/sequence.json",
    },
    {"mask": "coins_mask.png", "prefix": "coins_close15", "sequence": "config/sequence_close15.json"},
]


def with_label(image: np.ndarray, text: str, width: int = 320) -> np.ndarray:
    """Redimensiona a imagem e escreve um rótulo numa faixa branca em cima."""
    if image.ndim == 2:
        image = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
    height = round(image.shape[0] * width / image.shape[1])
    image = cv.resize(image, (width, height), interpolation=cv.INTER_NEAREST)
    band = np.full((28, width, 3), 255, dtype=np.uint8)
    cv.putText(band, text, (6, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv.LINE_AA)
    return np.vstack([band, image])


def stages_figure(prefix: str, summary: dict) -> Path:
    """Máscara inicial, cada estágio da sequência e a imagem de rótulos, lado a lado."""
    panels = [with_label(cv.imread(prefix + "_initial_mask.png", cv.IMREAD_UNCHANGED), "inicial")]
    for index, (stage, step) in enumerate(zip(summary["stages"], summary["sequence"]), start=1):
        text = "{0}. {1} {2} {3}x{3}".format(index, step["operation"], step["shape"], step["size"])
        panels.append(with_label(cv.imread(stage, cv.IMREAD_UNCHANGED), text))
    panels.append(with_label(cv.imread(prefix + "_labels.png"), "rotulos finais"))

    path = OUTPUT_DIR / (Path(prefix).name + "_estagios.png")
    cv.imwrite(str(path), np.hstack(panels))
    return path


def main() -> int:
    print("== reproducao das mascaras do M2.1")
    if lab_1_m2.main() != 0:
        return 1

    rows = []
    for item in ANALYSES:
        prefix = str(RESULTS_DIR / item["prefix"])
        print("== analyze " + item["mask"] + " com " + item["sequence"])
        code = pdi_lab(
            [
                "--input",
                str(OUTPUT_DIR / item["mask"]),
                "--output",
                prefix,
                "--operation",
                "analyze",
                "--sequence",
                item["sequence"],
                "--connectivity",
                str(CONNECTIVITY),
                "--min-area",
                str(MIN_AREA),
            ]
        )
        if code != 0:
            return code

        summary = json.loads(Path(prefix + "_summary.json").read_text(encoding="utf-8"))
        print("figura: " + str(stages_figure(prefix, summary)))

        before = summary["initial"]
        after = summary["final"]
        rows.append(
            [
                item["prefix"],
                Path(item["sequence"]).name,
                before["count_4"],
                before["count_8"],
                before["count_kept"],
                before["area_raw"],
                after["count_4"],
                after["count_8"],
                after["count_kept"],
                after["area_raw"],
            ]
        )

    with open(RESULTS_DIR / "comparison.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "analysis",
                "sequence",
                "initial_count_4",
                "initial_count_8",
                "initial_kept",
                "initial_area",
                "final_count_4",
                "final_count_8",
                "final_kept",
                "final_area",
            ]
        )
        writer.writerows(rows)

    print("tabela antes/depois em: " + str(RESULTS_DIR / "comparison.csv"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
