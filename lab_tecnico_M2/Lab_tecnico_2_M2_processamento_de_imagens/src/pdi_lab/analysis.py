"""Componentes conexos e sequencia morfologica do M2.2."""

import csv
import json
from pathlib import Path

import cv2 as cv
import numpy as np

from .errors import PdiLabError
from .segmentation import validate_mask

CONNECTIVITIES = [4, 8]

OPERATIONS = {
    "erode": cv.MORPH_ERODE,
    "dilate": cv.MORPH_DILATE,
    "open": cv.MORPH_OPEN,
    "close": cv.MORPH_CLOSE,
}

SHAPES = {
    "rect": cv.MORPH_RECT,
    "ellipse": cv.MORPH_ELLIPSE,
    "cross": cv.MORPH_CROSS,
}

CSV_HEADER = ["label", "area", "x", "y", "width", "height", "cx", "cy", "kept"]

# caixa verde = mantido pelo filtro de area, vermelha = filtrado
BOX_KEPT = (0, 200, 0)
BOX_FILTERED = (0, 0, 255)

# cores para pintar os componentes na imagem de rotulos
COLORS = [
    (230, 120, 40), (40, 200, 230), (60, 220, 60), (220, 60, 200), (60, 60, 230),
    (230, 230, 60), (140, 60, 230), (60, 160, 230), (230, 160, 160), (120, 230, 180),
]


def step_text(step):
    return "{} {} {}x{}, {} iteracao(oes)".format(
        step["operation"], step["shape"], step["size"], step["size"], step["iterations"])


def parse_steps(data):
    # confere a sequencia lida do json
    if not isinstance(data, dict) or not isinstance(data.get("steps"), list):
        raise PdiLabError("configuracao deve ter a chave 'steps' com uma lista")

    steps = []
    n = 0
    for item in data["steps"]:
        n += 1
        where = "passo " + str(n) + ": "
        if not isinstance(item, dict):
            raise PdiLabError(where + "cada passo deve ser um objeto")

        operation = item.get("operation")
        shape = item.get("shape")
        size = item.get("size")
        iterations = item.get("iterations", 1)
        purpose = item.get("purpose")

        if operation not in OPERATIONS:
            raise PdiLabError(where + "operacao desconhecida: " + str(operation)
                              + "; use erode, dilate, open ou close")
        if shape not in SHAPES:
            raise PdiLabError(where + "forma desconhecida: " + str(shape) + "; use rect, ellipse ou cross")
        # bool tambem e int no python, por isso o teste a mais
        if type(size) is not int or size < 3 or size % 2 == 0:
            raise PdiLabError(where + "size deve ser inteiro impar >= 3, recebido: " + str(size))
        if type(iterations) is not int or iterations < 1:
            raise PdiLabError(where + "iterations deve ser inteiro >= 1, recebido: " + str(iterations))
        if not isinstance(purpose, str) or purpose.strip() == "":
            raise PdiLabError(where + "informe em 'purpose' o defeito que o passo trata")

        steps.append({
            "operation": operation,
            "shape": shape,
            "size": size,
            "iterations": iterations,
            "purpose": purpose.strip(),
        })

    if len(steps) < 2:
        raise PdiLabError("a sequencia precisa de pelo menos duas operacoes")

    has_open_close = False
    for step in steps:
        if step["operation"] == "open" or step["operation"] == "close":
            has_open_close = True
    if not has_open_close:
        raise PdiLabError("a sequencia precisa incluir abertura ou fechamento")

    # o enunciado nao aceita repetir a mesma operacao sem motivo
    for i in range(1, len(steps)):
        a = steps[i - 1]
        b = steps[i]
        if (a["operation"] == b["operation"] and a["shape"] == b["shape"]
                and a["size"] == b["size"] and a["iterations"] == b["iterations"]):
            raise PdiLabError("dois passos seguidos identicos (" + step_text(b)
                              + "); junte em iterations ou mude o parametro")
    return steps


def load_sequence(path):
    path = Path(path)
    if not path.is_file():
        raise PdiLabError("arquivo de sequencia nao encontrado: " + str(path))
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise PdiLabError("arquivo de sequencia com JSON invalido: " + str(error))
    return parse_steps(data)


def require_binary_mask(image):
    if len(image.shape) != 2:
        raise PdiLabError("a entrada de analyze deve ser mascara de 1 canal; a imagem tem "
                          + str(image.shape[2]) + " canais")
    validate_mask(image, image.shape)
    return image


def apply_step(mask, step):
    size = step["size"]
    kernel = cv.getStructuringElement(SHAPES[step["shape"]], (size, size))
    return cv.morphologyEx(mask, OPERATIONS[step["operation"]], kernel, iterations=step["iterations"])


def label_components(mask, connectivity):
    # rotula os componentes; o rotulo 0 e o fundo e fica de fora
    if connectivity not in CONNECTIVITIES:
        raise PdiLabError("conectividade deve ser 4 ou 8, recebido: " + str(connectivity))

    binary = (mask == 255).astype(np.uint8)
    count, labels, stats, centroids = cv.connectedComponentsWithStats(binary, connectivity=connectivity)

    rows = []
    for label in range(1, count):
        rows.append({
            "label": label,
            "area": int(stats[label, cv.CC_STAT_AREA]),
            "x": int(stats[label, cv.CC_STAT_LEFT]),
            "y": int(stats[label, cv.CC_STAT_TOP]),
            "width": int(stats[label, cv.CC_STAT_WIDTH]),
            "height": int(stats[label, cv.CC_STAT_HEIGHT]),
            "cx": float(centroids[label][0]),
            "cy": float(centroids[label][1]),
        })
    return labels, rows


def apply_min_area(rows, min_area):
    if min_area < 0:
        raise PdiLabError("--min-area deve ser inteiro nao negativo, recebido: " + str(min_area))
    for row in rows:
        row["kept"] = row["area"] >= min_area
    return rows


def count_summary(rows):
    count_kept = 0
    area_raw = 0
    area_kept = 0
    for row in rows:
        area_raw += row["area"]
        if row["kept"]:
            count_kept += 1
            area_kept += row["area"]
    return {"count_raw": len(rows), "count_kept": count_kept, "area_raw": area_raw, "area_kept": area_kept}


def write_components_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(CSV_HEADER)
        for row in rows:
            kept = "true" if row["kept"] else "false"
            writer.writerow([row["label"], row["area"], row["x"], row["y"], row["width"], row["height"],
                             "%.2f" % row["cx"], "%.2f" % row["cy"], kept])
    return path


def labels_image(labels, rows):
    """Componentes coloridos, com caixa e numero do rotulo."""
    image = np.zeros((labels.shape[0], labels.shape[1], 3), dtype=np.uint8)
    for row in rows:
        image[labels == row["label"]] = COLORS[row["label"] % len(COLORS)]

    for row in rows:
        x, y, w, h = row["x"], row["y"], row["width"], row["height"]
        if row["kept"]:
            cv.rectangle(image, (x, y), (x + w - 1, y + h - 1), BOX_KEPT, 1)
            cv.putText(image, str(row["label"]), (x, max(y - 2, 10)), cv.FONT_HERSHEY_SIMPLEX,
                       0.35, (255, 255, 255), 1, cv.LINE_AA)
        else:
            cv.rectangle(image, (x, y), (x + w - 1, y + h - 1), BOX_FILTERED, 1)
    return image
