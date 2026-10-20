"""Gera todas as saidas do M2.1 de uma vez.

Uso: python lab_1_m2.py

Cada mascara tambem pode ser gerada pela linha de comando:
python -m pdi_lab --input <imagem> --output <mascara.png> --operation segment --method <metodo>
"""

import csv
import os
import sys

# deixa o script rodar de qualquer pasta, sem instalar o pacote
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))
os.chdir(PROJECT_ROOT)

import cv2 as cv  # noqa: E402
import numpy as np  # noqa: E402

from pdi_lab import segmentation  # noqa: E402
from pdi_lab.errors import PdiLabError  # noqa: E402
from pdi_lab.image_io import load_image, save_image  # noqa: E402

# a sobreposicao e so visualizacao; nas fotos de 10 megapixels cada PNG
# teria uns 13 MB, entao reduzo para 1280 no lado maior
OVERLAY_MAX_SIDE = 1280

# configuracoes de cada imagem. A moeda da foto e mais escura que o fundo,
# por isso o invert nos metodos em cinza. "selected" vai para o M2.2.
CASES = [
    {
        "image": "coins.png",
        "configs": [
            ("fixed", {"method": "fixed", "threshold": 120}),
            ("otsu", {"method": "otsu"}),
        ],
        "selected": "fixed",
        "sweep_invert": False,
        "sweep": range(90, 155, 5),
    },
    {
        "image": "moedas_real_separadas.jpg",
        "configs": [
            ("fixed", {"method": "fixed", "threshold": 85, "invert": True}),
            ("otsu", {"method": "otsu", "invert": True}),
            ("hsv", {"method": "hsv", "hsv_lower": (0, 30, 0), "hsv_upper": (179, 255, 255), "blur": 5}),
        ],
        "selected": "hsv",
        "sweep_invert": True,
        "sweep": range(60, 125, 5),
    },
]


def label_text(info):
    if info["method"] == "fixed":
        text = "fixed T=" + str(info["threshold"])
    elif info["method"] == "otsu":
        text = "otsu T=" + str(info["otsu_threshold"])
    else:
        text = "hsv S>=" + str(info["hsv_lower"][1])
    if info["blur"]:
        text += " blur " + str(info["blur"])
    if info["invert"]:
        text += " + invert"
    return text


def small(image):
    # reduz para caber em OVERLAY_MAX_SIDE; imagem pequena fica igual
    scale = OVERLAY_MAX_SIDE / max(image.shape[:2])
    if scale >= 1:
        return image
    w = round(image.shape[1] * scale)
    h = round(image.shape[0] * scale)
    return cv.resize(image, (w, h), interpolation=cv.INTER_AREA)


def panel(image, text, width=320):
    # imagem pequena com um titulo em cima, para montar a figura
    image = segmentation.to_bgr(image)
    height = round(image.shape[0] * width / image.shape[1])
    image = cv.resize(image, (width, height), interpolation=cv.INTER_AREA)
    band = np.full((28, width, 3), 255, dtype=np.uint8)
    cv.putText(band, text, (6, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv.LINE_AA)
    return np.vstack([band, image])


def main():
    os.makedirs("images/output", exist_ok=True)
    os.makedirs("results", exist_ok=True)

    foreground_rows = []
    sweep_rows = []

    try:
        for case in CASES:
            name = case["image"]
            stem = os.path.splitext(name)[0]
            image = load_image("images/input/" + name)
            print("== " + name)

            panels = [panel(image, "original")]
            masks = {}
            for config_name, config in case["configs"]:
                mask, info = segmentation.segment(image, **config)
                segmentation.validate_mask(mask, image.shape[:2])
                masks[config_name] = mask

                save_image("images/output/" + stem + "_mask_" + config_name + ".png", mask)
                save_image("images/output/" + stem + "_overlay_" + config_name + ".png",
                           small(segmentation.overlay(image, mask)))
                panels.append(panel(mask, label_text(info)))

                stats = segmentation.mask_stats(mask)
                threshold = info.get("threshold", info.get("otsu_threshold", ""))
                foreground_rows.append([name, config_name, threshold, info["invert"], info["blur"],
                                        stats["foreground"], stats["pixels"],
                                        "%.6f" % stats["foreground_ratio"], config_name == case["selected"]])
                print("%s: %s primeiro_plano=%.4f" % (config_name, label_text(info), stats["foreground_ratio"]))

            # mascara que vai para o M2.2
            chosen = masks[case["selected"]]
            save_image("images/output/" + stem + "_mask.png", chosen)

            panels.append(panel(segmentation.overlay(image, chosen), "sobreposicao " + case["selected"]))
            save_image("images/output/" + stem + "_comparacao.png", np.hstack(panels))

            # varredura do limiar fixo para ver a sensibilidade
            for t in case["sweep"]:
                mask, _ = segmentation.segment(image, "fixed", threshold=t, invert=case["sweep_invert"])
                stats = segmentation.mask_stats(mask)
                sweep_rows.append([name, t, case["sweep_invert"], stats["foreground"],
                                   "%.6f" % stats["foreground_ratio"]])
    except PdiLabError as error:
        print("erro: " + str(error), file=sys.stderr)
        return 1

    with open("results/foreground.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["image", "config", "threshold", "invert", "blur", "foreground", "pixels",
                         "foreground_ratio", "selected"])
        writer.writerows(foreground_rows)

    with open("results/threshold_sensitivity.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["image", "threshold", "invert", "foreground", "foreground_ratio"])
        writer.writerows(sweep_rows)

    print("imagens geradas em: images/output")
    print("tabelas em: results")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
