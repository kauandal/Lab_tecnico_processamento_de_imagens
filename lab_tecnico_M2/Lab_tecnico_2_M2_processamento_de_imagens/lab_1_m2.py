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

# Configurações de cada imagem. Todas passam pelo limiar fixo e pelo Otsu; a
# foto colorida também passa pelo HSV. ``selected`` é a que segue para o M2.2.
# Em moedas_real_separadas.jpg a moeda é mais escura que o fundo, por isso a
# inversão nos métodos em cinza.
CASES = [
    {
        "image": "coins.png",
        "configs": {
            "fixed": {"method": "fixed", "threshold": 120},
            "otsu": {"method": "otsu"},
        },
        "selected": "fixed",
        "sweep": {"invert": False, "thresholds": range(90, 155, 5)},
    },
    {
        "image": "moedas_real_separadas.jpg",
        "configs": {
            "fixed": {"method": "fixed", "threshold": 85, "invert": True},
            "otsu": {"method": "otsu", "invert": True},
            "hsv": {
                "method": "hsv",
                "hsv_lower": (0, 30, 0),
                "hsv_upper": (179, 255, 255),
                "blur": 5,
            },
        },
        "selected": "hsv",
        "sweep": {"invert": True, "thresholds": range(60, 125, 5)},
    },
]


def describe(details: dict) -> str:
    """Texto curto com o método e os parâmetros, para rótulos e tabela."""
    method = details["method"]
    if method == "fixed":
        text = "fixed T=" + str(details["threshold"])
    elif method == "otsu":
        text = "otsu T=" + str(details["otsu_threshold"])
    else:
        text = "hsv S>=" + str(details["hsv_lower"][1])
    if details["blur"]:
        text += " blur " + str(details["blur"])
    if details["invert"]:
        text += " + invert"
    return text


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
            print("== " + case["image"])

            panels = [with_label(image, "original")]
            masks = {}
            for name, config in case["configs"].items():
                result = segmentation.segment(image, **config)
                segmentation.validate_mask(result.mask, image.shape[:2])
                masks[name] = result.mask

                save_image(OUTPUT_DIR / (stem + "_mask_" + name + ".png"), result.mask)
                # A sobreposição é só visualização, então vai em JPEG para não
                # pesar; a máscara continua em PNG, sem perdas.
                save_image(
                    OUTPUT_DIR / (stem + "_overlay_" + name + ".jpg"),
                    segmentation.overlay(image, result.mask),
                )
                panels.append(with_label(result.mask, describe(result.details)))

                stats = segmentation.mask_stats(result.mask)
                threshold = result.details.get("threshold", result.details.get("otsu_threshold", ""))
                foreground_rows.append(
                    [
                        case["image"],
                        name,
                        threshold,
                        result.details["invert"],
                        result.details["blur"],
                        stats["foreground"],
                        stats["pixels"],
                        "{0:.6f}".format(stats["foreground_ratio"]),
                        name == case["selected"],
                    ]
                )
                print(
                    "{0}: {1} primeiro_plano={2:.4f}".format(
                        name, describe(result.details), stats["foreground_ratio"]
                    )
                )

            # Máscara de trabalho que segue para o M2.2.
            selected = masks[case["selected"]]
            save_image(OUTPUT_DIR / (stem + "_mask.png"), selected)

            panels.append(
                with_label(segmentation.overlay(image, selected), "sobreposicao " + case["selected"])
            )
            save_image(OUTPUT_DIR / (stem + "_comparacao.png"), np.hstack(panels))

            # Varredura do limiar fixo, para medir a sensibilidade do parâmetro.
            for threshold in case["sweep"]["thresholds"]:
                mask = segmentation.segment(
                    image, "fixed", threshold=threshold, invert=case["sweep"]["invert"]
                ).mask
                stats = segmentation.mask_stats(mask)
                sweep_rows.append(
                    [
                        case["image"],
                        threshold,
                        case["sweep"]["invert"],
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
            ["image", "config", "threshold", "invert", "blur", "foreground", "pixels", "foreground_ratio", "selected"]
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
