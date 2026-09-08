"""Reproduz todas as saídas do laboratório M1.3 em uma única execução.

Este script é um atalho de reprodução. A implementação avaliada está em
``src/pdi_lab``, e cada operação também pode ser executada isoladamente pela
linha de comando::

    python -m pdi_lab --input <arquivo> --output <arquivo> --operation <nome>

Uso::

    python lab_3_m1.py [--input images/input/aura.png]
                       [--output-dir images/output]
                       [--results-dir results]
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Os caminhos deste script sao relativos a raiz do projeto, de forma que ele
# funcione a partir de qualquer diretorio de trabalho.
os.chdir(PROJECT_ROOT)

from pdi_lab import kernels, operations  # noqa: E402
from pdi_lab.errors import PdiLabError  # noqa: E402
from pdi_lab.image_io import load_image, save_image  # noqa: E402

DEFAULT_INPUT = "images/input/aura.png"
DEFAULT_OUTPUT_DIR = "images/output"
DEFAULT_RESULTS_DIR = "results"
INPUT_DIR = "images/input"

SYNTHETIC_SIZE = 16

SUMMARY_HEADER = (
    "response,border,pixels,min,max,mean,negatives,zeros,positives,outside_8bit"
)


def build_vertical_step(size: int = SYNTHETIC_SIZE) -> np.ndarray:
    """Degrau vertical: metade esquerda escura, metade direita clara."""
    image = np.zeros((size, size), dtype=np.uint8)
    for y in range(size):
        for x in range(size // 2, size):
            image[y, x] = 255
    return image


def build_horizontal_step(size: int = SYNTHETIC_SIZE) -> np.ndarray:
    """Degrau horizontal: metade superior escura, metade inferior clara."""
    image = np.zeros((size, size), dtype=np.uint8)
    for y in range(size // 2, size):
        for x in range(size):
            image[y, x] = 255
    return image


def build_impulse(size: int = SYNTHETIC_SIZE) -> np.ndarray:
    """Imagem preta com um único pixel de valor 255 no centro."""
    image = np.zeros((size, size), dtype=np.uint8)
    image[size // 2, size // 2] = 255
    return image


def build_shapes(size: int = SYNTHETIC_SIZE) -> np.ndarray:
    """Formas simples, com conteúdo encostado na borda esquerda e superior."""
    image = np.zeros((size, size), dtype=np.uint8)
    for y in range(size):
        for x in range(2):
            image[y, x] = 255  # barra colada na borda esquerda
    for y in range(2):
        for x in range(size):
            image[y, x] = 180  # faixa colada na borda superior
    for y in range(size // 2, size // 2 + 4):
        for x in range(size // 2, size // 2 + 4):
            image[y, x] = 120  # quadrado isolado no interior
    return image


def write_matrix_csv(raw: np.ndarray, path: Path) -> None:
    """Grava uma matriz de resposta bruta em CSV, uma linha por linha."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        ",".join("{0:.4f}".format(value) for value in row)
        for row in raw.tolist()
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def summary_row(name: str, border: str, raw: np.ndarray) -> str:
    """Monta uma linha do resumo estatístico da resposta bruta."""
    stats = operations.response_summary(raw)
    return ",".join(
        [
            name,
            border,
            str(stats["pixels"]),
            "{0:.4f}".format(stats["min"]),
            "{0:.4f}".format(stats["max"]),
            "{0:.4f}".format(stats["mean"]),
            str(stats["negatives"]),
            str(stats["zeros"]),
            str(stats["positives"]),
            str(stats["outside_8bit"]),
        ]
    )


def border_profile(copy: np.ndarray, replicate: np.ndarray, radius: int) -> list[str]:
    """Compara as duas estratégias por distância até a borda da imagem.

    Espera-se que a diferença se concentre numa faixa cuja largura corresponde
    ao raio do kernel. Se a imagem inteira mudar, há erro de índices.
    """
    height, width = copy.shape[0], copy.shape[1]
    difference = np.abs(copy - replicate)

    lines = ["distance_from_border,pixels,mean_abs_diff,max_abs_diff"]
    limit = min(radius + 3, min(height, width) // 2)

    for distance in range(limit):
        values = []
        for y in range(height):
            for x in range(width):
                if min(x, y, width - 1 - x, height - 1 - y) == distance:
                    values.append(difference[y, x])
        if not values:
            continue
        lines.append(
            ",".join(
                [
                    str(distance),
                    str(len(values)),
                    "{0:.4f}".format(sum(values) / len(values)),
                    "{0:.4f}".format(max(values)),
                ]
            )
        )

    return lines


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--results-dir", default=DEFAULT_RESULTS_DIR)
    return parser.parse_args(argv)


def run_real_image(image: np.ndarray, output_dir: Path) -> dict:
    """Aplica todas as operações à imagem real e grava as visualizações."""
    responses = {}

    save_image(output_dir / "gray_weighted.png", image)

    responses[("identity", "replicate")] = operations.convolve(
        image, kernels.IDENTITY_3X3, operations.BORDER_REPLICATE
    )
    responses[("mean_3x3", "replicate")] = operations.mean_filter(
        image, 3, operations.BORDER_REPLICATE
    )
    responses[("mean_3x3", "copy")] = operations.mean_filter(
        image, 3, operations.BORDER_COPY
    )
    responses[("mean_5x5", "replicate")] = operations.mean_filter(
        image, 5, operations.BORDER_REPLICATE
    )
    responses[("weighted_mean_3x3", "replicate")] = operations.weighted_mean(
        image, operations.BORDER_REPLICATE
    )
    responses[("laplacian", "replicate")] = operations.laplacian(
        image, operations.BORDER_REPLICATE
    )

    gradient = operations.sobel(image, operations.BORDER_REPLICATE)
    for component in ("gx", "gy", "l1", "l2"):
        responses[("sobel_" + component, "replicate")] = gradient[component]

    # Suavizacao e convolucao generica: a resposta ja esta na faixa de 8 bits.
    for name in ("identity", "mean_3x3", "mean_5x5", "weighted_mean_3x3"):
        save_image(
            output_dir / (name + "_replicate.png"),
            operations.to_uint8(responses[(name, "replicate")]),
        )
    save_image(
        output_dir / "mean_3x3_copy.png",
        operations.to_uint8(responses[("mean_3x3", "copy")]),
    )

    # Laplaciano: tres visualizacoes da mesma resposta bruta.
    laplacian_raw = responses[("laplacian", "replicate")]
    for view in (
        operations.VIEW_OFFSET_NAME,
        operations.VIEW_ABS,
        operations.VIEW_NORMALIZE,
    ):
        save_image(
            output_dir / ("laplacian_" + view + "_replicate.png"),
            operations.to_uint8(laplacian_raw, view),
        )

    save_image(
        output_dir / "laplacian_enhance_replicate.png",
        operations.laplacian_enhance(image, operations.BORDER_REPLICATE, 1.0),
    )

    # Sobel: componentes com deslocamento, magnitudes saturadas e normalizadas.
    for component in ("gx", "gy"):
        save_image(
            output_dir / ("sobel_" + component + "_replicate.png"),
            operations.to_uint8(
                responses[("sobel_" + component, "replicate")],
                operations.VIEW_OFFSET_NAME,
            ),
        )
    for component in ("l1", "l2"):
        raw = responses[("sobel_" + component, "replicate")]
        save_image(
            output_dir / ("sobel_" + component + "_replicate.png"),
            operations.to_uint8(raw, operations.VIEW_CLAMP),
        )
        save_image(
            output_dir / ("sobel_" + component + "_normalize_replicate.png"),
            operations.to_uint8(raw, operations.VIEW_NORMALIZE),
        )

    return responses


def run_synthetic(output_dir: Path, results_dir: Path) -> dict:
    """Gera os casos sintéticos e as evidências numéricas correspondentes."""
    responses = {}
    synthetic = {
        "step_vertical": build_vertical_step(),
        "step_horizontal": build_horizontal_step(),
        "impulse": build_impulse(),
        "shapes": build_shapes(),
    }

    for name, image in synthetic.items():
        save_image(Path(INPUT_DIR) / (name + ".png"), image)

    # Resposta ao impulso: cada uma das nove posicoes recebe 255/9.
    impulse_mean = operations.mean_filter(
        synthetic["impulse"], 3, operations.BORDER_REPLICATE
    )
    write_matrix_csv(impulse_mean, results_dir / "raw_impulse_mean_3x3.csv")
    save_image(
        output_dir / "impulse_mean_3x3_replicate.png",
        operations.to_uint8(impulse_mean),
    )
    responses[("impulse_mean_3x3", "replicate")] = impulse_mean

    # Degraus: Gx responde ao vertical, Gy responde ao horizontal.
    for name in ("step_vertical", "step_horizontal"):
        gradient = operations.sobel(synthetic[name], operations.BORDER_REPLICATE)
        for component in ("gx", "gy"):
            responses[(name + "_" + component, "replicate")] = gradient[component]
        write_matrix_csv(
            gradient["gx"], results_dir / ("raw_" + name + "_gx.csv")
        )
        write_matrix_csv(
            gradient["gy"], results_dir / ("raw_" + name + "_gy.csv")
        )
        save_image(
            output_dir / (name + "_sobel_gx_replicate.png"),
            operations.to_uint8(gradient["gx"], operations.VIEW_OFFSET_NAME),
        )
        save_image(
            output_dir / (name + "_sobel_gy_replicate.png"),
            operations.to_uint8(gradient["gy"], operations.VIEW_OFFSET_NAME),
        )

    # Laplaciano no degrau: sinais opostos dos dois lados da transicao.
    step_laplacian = operations.laplacian(
        synthetic["step_vertical"], operations.BORDER_REPLICATE
    )
    write_matrix_csv(step_laplacian, results_dir / "raw_step_vertical_laplacian.csv")
    responses[("step_vertical_laplacian", "replicate")] = step_laplacian

    # Comparacao de bordas numa imagem com conteudo encostado na moldura.
    shapes = synthetic["shapes"]
    for size in (3, 5):
        com_copy = operations.mean_filter(shapes, size, operations.BORDER_COPY)
        com_replicate = operations.mean_filter(
            shapes, size, operations.BORDER_REPLICATE
        )
        responses[("shapes_mean_" + str(size), "copy")] = com_copy
        responses[("shapes_mean_" + str(size), "replicate")] = com_replicate

        save_image(
            output_dir / ("shapes_mean_" + str(size) + "_copy.png"),
            operations.to_uint8(com_copy),
        )
        save_image(
            output_dir / ("shapes_mean_" + str(size) + "_replicate.png"),
            operations.to_uint8(com_replicate),
        )

        lines = border_profile(com_copy, com_replicate, size // 2)
        (results_dir / ("border_profile_mean_" + str(size) + ".csv")).write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )

    return responses


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    output_dir = Path(args.output_dir)
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    try:
        image = operations.to_grayscale(load_image(args.input))

        responses = run_real_image(image, output_dir)
        responses.update(run_synthetic(output_dir, results_dir))

        lines = [SUMMARY_HEADER]
        for (name, border), raw in responses.items():
            lines.append(summary_row(name, border, raw))
        (results_dir / "summary.csv").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )
        print("\n".join(lines))
    except PdiLabError as error:
        print("erro: " + str(error), file=sys.stderr)
        return 1

    print("imagens geradas em: " + str(output_dir))
    print("respostas brutas e resumo em: " + str(results_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
