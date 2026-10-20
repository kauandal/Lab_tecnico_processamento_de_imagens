"""Reproduz todas as saídas do laboratório M1.2 em uma única execução.

Este script é um atalho de reprodução. A implementação avaliada está em
``src/pdi_lab``, e cada operação também pode ser executada isoladamente pela
linha de comando::

    python -m pdi_lab --input <arquivo> --output <arquivo> --operation <nome>

Uso::

    python lab_2_m1.py [--input images/input/aura.png]
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

from pdi_lab import operations  # noqa: E402
from pdi_lab.errors import PdiLabError  # noqa: E402
from pdi_lab.image_io import load_image, save_image  # noqa: E402

DEFAULT_INPUT = "images/input/aura.png"
DEFAULT_OUTPUT_DIR = "images/output"
DEFAULT_RESULTS_DIR = "results"

RAMP_PATH = "images/input/ramp.png"
RAMP_HEIGHT = 64

BRIGHTNESS_VALUES = (50, -50)
CONTRAST_ALPHAS = (0.5, 1.0, 1.5)
THRESHOLDS = (128, 64)


def build_ramp(height: int = RAMP_HEIGHT) -> np.ndarray:
    """Gera uma rampa sintética de 256 colunas, uma por intensidade.

    O histograma dessa imagem é uniforme, com exatamente ``height`` pixels em
    cada intensidade, o que torna trivial conferir à mão o efeito de cada
    transformação sobre a distribuição.
    """
    ramp = np.zeros((height, 256), dtype=np.uint8)
    for y in range(height):
        ramp[y] = list(range(256))
    return ramp


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--results-dir", default=DEFAULT_RESULTS_DIR)
    return parser.parse_args(argv)


def write_histogram(counts: list[int], path: Path) -> None:
    """Grava o histograma em CSV no formato definido pelo contrato."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(operations.format_histogram(counts) + "\n", encoding="utf-8")


def summary_row(name: str, counts: list[int]) -> str:
    """Monta uma linha do resumo estatístico a partir do histograma."""
    stats = operations.histogram_summary(counts)
    return ",".join(
        [
            name,
            str(stats["pixels"]),
            "{0:.4f}".format(stats["mean"]),
            "{0:.4f}".format(stats["stddev"]),
            str(stats["min"]),
            str(stats["max"]),
            str(stats["levels_used"]),
            str(stats["at_zero"]),
            str(stats["at_max"]),
        ]
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    output_dir = Path(args.output_dir)
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    try:
        original = operations.to_grayscale(load_image(args.input))
        save_image(output_dir / "gray_weighted.png", original)

        transformadas = {}

        for value in BRIGHTNESS_VALUES:
            nome = "brightness_pos" if value > 0 else "brightness_neg"
            nome = nome + str(abs(value))
            transformadas[nome] = operations.brightness(original, value)

        for alpha in CONTRAST_ALPHAS:
            nome = "contrast_" + str(alpha).replace(".", "_")
            transformadas[nome] = operations.contrast(original, alpha)

        transformadas["negative"] = operations.negative(original)

        for limiar in THRESHOLDS:
            transformadas["threshold_" + str(limiar)] = operations.threshold(
                original, limiar
            )

        for nome, imagem in transformadas.items():
            save_image(output_dir / (nome + ".png"), imagem)

        # Histograma da original e de todas as transformadas. O enunciado pede
        # a original e ao menos duas transformadas; o CSV e gravado para todas
        # porque o custo e baixo e a comparacao fica completa.
        histogramas = {"original": operations.histogram(original)}
        for nome, imagem in transformadas.items():
            histogramas[nome] = operations.histogram(imagem)

        for nome, counts in histogramas.items():
            write_histogram(counts, results_dir / ("histogram_" + nome + ".csv"))

        # Imagem sintetica de histograma uniforme, usada na analise.
        ramp = build_ramp()
        save_image(RAMP_PATH, ramp)
        ramp_counts = operations.histogram(ramp)
        write_histogram(ramp_counts, results_dir / "histogram_ramp.csv")
        histogramas["ramp"] = ramp_counts
        histogramas["ramp_brightness_pos50"] = operations.histogram(
            operations.brightness(ramp, 50)
        )
        histogramas["ramp_contrast_1_5"] = operations.histogram(
            operations.contrast(ramp, 1.5)
        )

        linhas = [
            "image,pixels,mean,stddev,min,max,levels_used,at_zero,at_max"
        ]
        for nome, counts in histogramas.items():
            linhas.append(summary_row(nome, counts))
        (results_dir / "summary.csv").write_text(
            "\n".join(linhas) + "\n", encoding="utf-8"
        )
        print("\n".join(linhas))
    except PdiLabError as error:
        print("erro: " + str(error), file=sys.stderr)
        return 1

    print("imagens geradas em: " + str(output_dir))
    print("histogramas e resumo em: " + str(results_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
