"""Gera todas as saidas do M2.2 de uma vez.

Uso: python lab_2_m2.py

Primeiro refaz as mascaras do M2.1 (lab_1_m2.py), depois gera a mascara das
moedas empilhadas e roda o analyze nas tres mascaras. Cada analise tambem
pode ser feita pela linha de comando:
python -m pdi_lab --input <mascara.png> --output <prefixo> --operation analyze --sequence <config.json>
"""

import csv
import json
import os
import sys

# deixa o script rodar de qualquer pasta, sem instalar o pacote
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
os.chdir(PROJECT_ROOT)

import cv2 as cv  # noqa: E402
import numpy as np  # noqa: E402

import lab_1_m2  # noqa: E402
from pdi_lab.cli import main as pdi_lab  # noqa: E402

# a foto das moedas empilhadas nao entra no estudo do M2.1, entao a mascara
# dela e feita aqui: Otsu invertido com suavizacao 5
STACKED_SEGMENT = [
    "--input", "images/input/moedas_real_empilhadas.jpg",
    "--output", "images/output/moedas_real_empilhadas_mask.png",
    "--operation", "segment", "--method", "otsu", "--invert", "--blur", "5",
]

# mascara, prefixo da saida, sequencia e area minima (mais ou menos metade
# da menor moeda de cada imagem)
ANALYSES = [
    ("coins_mask.png", "coins", "config/coins.json", 500),
    ("moedas_real_separadas_mask.png", "moedas_real_separadas", "config/moedas_real.json", 50000),
    ("moedas_real_empilhadas_mask.png", "moedas_real_empilhadas", "config/moedas_real.json", 50000),
]


def panel(image, text, width=320):
    if len(image.shape) == 2:
        image = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
    height = round(image.shape[0] * width / image.shape[1])
    image = cv.resize(image, (width, height), interpolation=cv.INTER_AREA)
    band = np.full((28, width, 3), 255, dtype=np.uint8)
    cv.putText(band, text, (6, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv.LINE_AA)
    return np.vstack([band, image])


def main():
    print("== reproducao das mascaras do M2.1")
    if lab_1_m2.main() != 0:
        return 1

    print("== mascara das moedas empilhadas")
    if pdi_lab(STACKED_SEGMENT) != 0:
        return 1

    rows = []
    for mask_name, name, sequence, min_area in ANALYSES:
        prefix = "results/" + name
        print("== analyze " + mask_name + " com " + sequence)
        code = pdi_lab(["--input", "images/output/" + mask_name, "--output", prefix,
                        "--operation", "analyze", "--sequence", sequence,
                        "--connectivity", "8", "--min-area", str(min_area)])
        if code != 0:
            return code

        with open(prefix + "_summary.json", encoding="utf-8") as file:
            summary = json.load(file)

        # figura: mascara inicial, cada estagio e os rotulos finais
        panels = [panel(cv.imread(prefix + "_initial_mask.png", cv.IMREAD_UNCHANGED), "inicial")]
        n = 0
        for stage, step in zip(summary["stages"], summary["sequence"]):
            n += 1
            text = "%d. %s %s %dx%d" % (n, step["operation"], step["shape"], step["size"], step["size"])
            panels.append(panel(cv.imread(stage, cv.IMREAD_UNCHANGED), text))
        panels.append(panel(cv.imread(prefix + "_labels.png"), "rotulos finais"))
        cv.imwrite("images/output/" + name + "_estagios.png", np.hstack(panels))
        print("figura: images/output/" + name + "_estagios.png")

        before = summary["initial"]
        after = summary["final"]
        rows.append([name, os.path.basename(sequence), min_area,
                     before["count_4"], before["count_8"], before["count_kept"], before["area_raw"],
                     after["count_4"], after["count_8"], after["count_kept"], after["area_raw"]])

    with open("results/comparison.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["analysis", "sequence", "min_area", "initial_count_4", "initial_count_8",
                         "initial_kept", "initial_area", "final_count_4", "final_count_8",
                         "final_kept", "final_area"])
        writer.writerows(rows)

    print("tabela antes/depois em: results/comparison.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
