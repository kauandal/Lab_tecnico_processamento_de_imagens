"""Reproduz todas as saídas do laboratório M2.1 em uma única execução.

Este script é um atalho de reprodução. A implementação avaliada está em
``src/pdi_lab``, e cada máscara também pode ser gerada isoladamente pela
linha de comando::

    python -m pdi_lab --input <imagem> --output <mascara.png> --operation segment --method <metodo>

Uso::

    python lab_1_m2.py
"""

from __future__ import annotations

import csv
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

from pdi_lab import segmentation  # noqa: E402
from pdi_lab.errors import PdiLabError  # noqa: E402
from pdi_lab.image_io import load_image, save_image  # noqa: E402

INPUT_DIR = Path("images/input")
OUTPUT_DIR = Path("images/output")
RESULTS_DIR = Path("results")

# Em coins.png a moeda é mais clara que o fundo. Em moedas_brasileiras.jpg ela
# é mais escura que o fundo branco, por isso a inversão.
CASES = [
    {"image": "coins.png", "threshold": 120, "invert": False, "sweep": range(90, 155, 5)},
    {"image": "moedas_brasileiras.jpg", "threshold": 230, "invert": True, "sweep": range(190, 255, 5)},
]

# Configuração escolhida para seguir para o M2.2 nas duas imagens.
SELECTED = "fixed"


def run_config(image: np.ndarray, case: dict, method: str):
    """Segmenta com o método pedido e confere a máscara antes de devolver."""
    threshold = case["threshold"] if method == "fixed" else None
    result = segmentation.segment(
        image, method, threshold=threshold, invert=case["invert"]
    )
    segmentation.validate_mask(result.mask, image.shape[:2])
    return result


def with_label(image: np.ndarray, text: str, width: int = 320) -> np.ndarray:
    """Redimensiona a imagem e escreve um rótulo numa faixa branca em cima."""
    image = segmentation.to_bgr(image)
    height = round(image.shape[0] * width / image.shape[1])
    image = cv.resize(image, (width, height), interpolation=cv.INTER_AREA)
    band = np.full((28, width, 3), 255, dtype=np.uint8)
    cv.putText(band, text, (6, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv.LINE_AA)
    return np.vstack([band, image])


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    foreground_rows = []
    sweep_rows = []

    try:
        for case in CASES:
            stem = Path(case["image"]).stem
            image = load_image(INPUT_DIR / case["image"])
            suffix = " + invert" if case["invert"] else ""
            print("== " + case["image"])

            masks = {}
            labels = {}
            for method in ("fixed", "otsu"):
                result = run_config(image, case, method)
                masks[method] = result.mask
                threshold = result.details.get("threshold", result.details.get("otsu_threshold"))
                labels[method] = method + " T=" + str(threshold) + suffix

                save_image(OUTPUT_DIR / (stem + "_mask_" + method + ".png"), result.mask)
                save_image(
                    OUTPUT_DIR / (stem + "_overlay_" + method + ".png"),
                    segmentation.overlay(image, result.mask),
                )

                stats = segmentation.mask_stats(result.mask)
                foreground_rows.append(
                    [
                        case["image"],
                        method,
                        threshold,
                        case["invert"],
                        stats["foreground"],
                        stats["pixels"],
                        "{0:.6f}".format(stats["foreground_ratio"]),
                        method == SELECTED,
                    ]
                )
                print(
                    "{0}: limiar={1} primeiro_plano={2:.4f}".format(
                        method, threshold, stats["foreground_ratio"]
                    )
                )

            # Máscara de trabalho que segue para o M2.2.
            save_image(OUTPUT_DIR / (stem + "_mask.png"), masks[SELECTED])

            panels = [
                with_label(image, "original"),
                with_label(masks["fixed"], labels["fixed"]),
                with_label(masks["otsu"], labels["otsu"]),
                with_label(segmentation.overlay(image, masks[SELECTED]), "sobreposicao " + SELECTED),
            ]
            save_image(OUTPUT_DIR / (stem + "_comparacao.png"), np.hstack(panels))

            # Varredura do limiar fixo, para medir a sensibilidade do parâmetro.
            for threshold in case["sweep"]:
                mask = segmentation.segment(
                    image, "fixed", threshold=threshold, invert=case["invert"]
                ).mask
                stats = segmentation.mask_stats(mask)
                sweep_rows.append(
                    [
                        case["image"],
                        threshold,
                        case["invert"],
                        stats["foreground"],
                        "{0:.6f}".format(stats["foreground_ratio"]),
                    ]
                )
    except PdiLabError as error:
        print("erro: " + str(error), file=sys.stderr)
        return 1

    with open(RESULTS_DIR / "foreground.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["image", "method", "threshold", "invert", "foreground", "pixels", "foreground_ratio", "selected"]
        )
        writer.writerows(foreground_rows)

    with open(RESULTS_DIR / "threshold_sensitivity.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["image", "threshold", "invert", "foreground", "foreground_ratio"])
        writer.writerows(sweep_rows)

    print("imagens geradas em: " + str(OUTPUT_DIR))
    print("tabelas em: " + str(RESULTS_DIR))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
