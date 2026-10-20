"""Componentes conexos e sequência morfológica sobre máscaras binárias.

A máscara de entrada segue a convenção do M2.1: 255 é objeto e 0 é fundo. A
rotulação e a morfologia usam as funções do OpenCV, como o enunciado permite.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

import cv2 as cv
import numpy as np

from .errors import PdiLabError
from .segmentation import FOREGROUND, validate_mask

CONNECTIVITIES = (4, 8)

MORPH_OPERATIONS = {
    "erode": cv.MORPH_ERODE,
    "dilate": cv.MORPH_DILATE,
    "open": cv.MORPH_OPEN,
    "close": cv.MORPH_CLOSE,
}

KERNEL_SHAPES = {
    "rect": cv.MORPH_RECT,
    "ellipse": cv.MORPH_ELLIPSE,
    "cross": cv.MORPH_CROSS,
}

CSV_HEADER = ["label", "area", "x", "y", "width", "height", "cx", "cy", "kept"]

# Cores BGR das caixas: verde para componente mantido, vermelho para filtrado.
BOX_KEPT = (0, 200, 0)
BOX_FILTERED = (0, 0, 255)


@dataclass
class Step:
    """Uma operação da sequência morfológica."""

    operation: str
    shape: str
    size: int
    iterations: int
    purpose: str

    def describe(self) -> str:
        return "{0} {1} {2}x{2}, {3} iteracao(oes)".format(
            self.operation, self.shape, self.size, self.iterations
        )

    def as_dict(self) -> dict:
        return {
            "operation": self.operation,
            "shape": self.shape,
            "size": self.size,
            "iterations": self.iterations,
            "purpose": self.purpose,
        }


def parse_steps(data) -> list[Step]:
    """Valida a sequência lida do arquivo de configuração."""
    if not isinstance(data, dict) or not isinstance(data.get("steps"), list):
        raise PdiLabError("configuracao deve ter a chave 'steps' com uma lista")

    steps = []
    for index, item in enumerate(data["steps"], start=1):
        where = "passo " + str(index) + ": "
        if not isinstance(item, dict):
            raise PdiLabError(where + "cada passo deve ser um objeto")

        operation = item.get("operation")
        shape = item.get("shape")
        size = item.get("size")
        iterations = item.get("iterations", 1)
        purpose = item.get("purpose")

        if operation not in MORPH_OPERATIONS:
            raise PdiLabError(
                where + "operacao desconhecida: " + str(operation)
                + "; use " + ", ".join(MORPH_OPERATIONS)
            )
        if shape not in KERNEL_SHAPES:
            raise PdiLabError(
                where + "forma desconhecida: " + str(shape)
                + "; use " + ", ".join(KERNEL_SHAPES)
            )
        if not isinstance(size, int) or isinstance(size, bool) or size < 3 or size % 2 == 0:
            raise PdiLabError(where + "size deve ser inteiro impar >= 3, recebido: " + str(size))
        if (
            not isinstance(iterations, int)
            or isinstance(iterations, bool)
            or iterations < 1
        ):
            raise PdiLabError(where + "iterations deve ser inteiro >= 1, recebido: " + str(iterations))
        if not isinstance(purpose, str) or not purpose.strip():
            raise PdiLabError(where + "informe em 'purpose' o defeito que o passo trata")

        steps.append(Step(operation, shape, size, iterations, purpose.strip()))

    if len(steps) < 2:
        raise PdiLabError("a sequencia precisa de pelo menos duas operacoes")
    if not any(step.operation in ("open", "close") for step in steps):
        raise PdiLabError("a sequencia precisa incluir abertura ou fechamento")
    for previous, current in zip(steps, steps[1:]):
        if (previous.operation, previous.shape, previous.size, previous.iterations) == (
            current.operation,
            current.shape,
            current.size,
            current.iterations,
        ):
            raise PdiLabError(
                "dois passos seguidos identicos (" + current.describe()
                + "); junte em iterations ou mude o parametro"
            )
    return steps


def load_sequence(path: str | Path) -> list[Step]:
    """Lê a sequência morfológica de um arquivo JSON."""
    path = Path(path)
    if not path.is_file():
        raise PdiLabError("arquivo de sequencia nao encontrado: " + str(path))
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise PdiLabError("arquivo de sequencia com JSON invalido: " + str(error)) from None
    return parse_steps(data)


def require_binary_mask(image: np.ndarray) -> np.ndarray:
    """Recusa entrada que não seja máscara de um canal com valores {0, 255}."""
    if image.ndim != 2:
        raise PdiLabError(
            "a entrada de analyze deve ser mascara de 1 canal; a imagem tem "
            + str(image.shape[2]) + " canais"
        )
    validate_mask(image, image.shape)
    return image


def apply_step(mask: np.ndarray, step: Step) -> np.ndarray:
    """Aplica uma operação morfológica com o elemento estruturante do passo."""
    kernel = cv.getStructuringElement(KERNEL_SHAPES[step.shape], (step.size, step.size))
    return cv.morphologyEx(
        mask, MORPH_OPERATIONS[step.operation], kernel, iterations=step.iterations
    )


def label_components(mask: np.ndarray, connectivity: int):
    """Rotula os componentes de primeiro plano, sem o rótulo de fundo.

    Devolve a matriz de rótulos e uma linha por componente com área, caixa
    delimitadora e centroide.
    """
    if connectivity not in CONNECTIVITIES:
        raise PdiLabError("conectividade deve ser 4 ou 8, recebido: " + str(connectivity))

    binary = (mask == FOREGROUND).astype(np.uint8)
    count, labels, stats, centroids = cv.connectedComponentsWithStats(
        binary, connectivity=connectivity
    )

    rows = []
    for label in range(1, count):
        rows.append(
            {
                "label": label,
                "area": int(stats[label, cv.CC_STAT_AREA]),
                "x": int(stats[label, cv.CC_STAT_LEFT]),
                "y": int(stats[label, cv.CC_STAT_TOP]),
                "width": int(stats[label, cv.CC_STAT_WIDTH]),
                "height": int(stats[label, cv.CC_STAT_HEIGHT]),
                "cx": float(centroids[label][0]),
                "cy": float(centroids[label][1]),
            }
        )
    return labels, rows


def apply_min_area(rows: list[dict], min_area: int) -> list[dict]:
    """Marca em ``kept`` os componentes com área maior ou igual a ``min_area``."""
    if min_area < 0:
        raise PdiLabError("--min-area deve ser inteiro nao negativo, recebido: " + str(min_area))
    for row in rows:
        row["kept"] = row["area"] >= min_area
    return rows


def count_summary(rows: list[dict]) -> dict:
    """Contagens e áreas brutas e após o filtro."""
    kept = [row for row in rows if row["kept"]]
    return {
        "count_raw": len(rows),
        "count_kept": len(kept),
        "area_raw": sum(row["area"] for row in rows),
        "area_kept": sum(row["area"] for row in kept),
    }


def write_components_csv(path: str | Path, rows: list[dict]) -> Path:
    """Grava o CSV de componentes, uma linha por componente."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(CSV_HEADER)
        for row in rows:
            writer.writerow(
                [
                    row["label"],
                    row["area"],
                    row["x"],
                    row["y"],
                    row["width"],
                    row["height"],
                    "{0:.2f}".format(row["cx"]),
                    "{0:.2f}".format(row["cy"]),
                    "true" if row["kept"] else "false",
                ]
            )
    return path


def label_color(label: int) -> tuple[int, int, int]:
    """Cor fixa por rótulo, para a imagem sair igual em toda execução."""
    hue = (label * 37) % 180
    hsv = np.uint8([[[hue, 200, 230]]])
    b, g, r = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)[0, 0]
    return int(b), int(g), int(r)


def labels_image(labels: np.ndarray, rows: list[dict]) -> np.ndarray:
    """Componentes coloridos com caixa e número do rótulo.

    Caixa verde: componente mantido pelo filtro de área. Caixa vermelha:
    componente descartado.
    """
    image = np.zeros(labels.shape + (3,), dtype=np.uint8)
    for row in rows:
        image[labels == row["label"]] = label_color(row["label"])

    for row in rows:
        color = BOX_KEPT if row["kept"] else BOX_FILTERED
        top_left = (row["x"], row["y"])
        bottom_right = (row["x"] + row["width"] - 1, row["y"] + row["height"] - 1)
        cv.rectangle(image, top_left, bottom_right, color, 1)
        if row["kept"]:
            cv.putText(
                image,
                str(row["label"]),
                (row["x"], max(row["y"] - 2, 10)),
                cv.FONT_HERSHEY_SIMPLEX,
                0.35,
                (255, 255, 255),
                1,
                cv.LINE_AA,
            )
    return image
