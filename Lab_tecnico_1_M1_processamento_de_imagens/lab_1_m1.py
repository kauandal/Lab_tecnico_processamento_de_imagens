"""Reproduz todas as saídas do laboratório M1.1 em uma única execução.

Este script é um atalho de reprodução. A implementação avaliada está em
``src/pdi_lab``, e cada operação também pode ser executada isoladamente pela
linha de comando::

    python -m pdi_lab --input <arquivo> --output <arquivo> --operation <nome>

Uso::

    python lab_1_m1.py [--input images/input/aura_small.png]
                       [--output-dir images/output]
                       [--results-dir results]
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Os caminhos deste script sao relativos a raiz do projeto, de forma que ele
# funcione a partir de qualquer diretorio de trabalho.
os.chdir(PROJECT_ROOT)

from pdi_lab import operations  # noqa: E402
from pdi_lab.errors import PdiLabError  # noqa: E402
from pdi_lab.image_io import load_image, save_image  # noqa: E402

DEFAULT_INPUT = "images/input/aura_small.png"
DEFAULT_OUTPUT_DIR = "images/output"
DEFAULT_RESULTS_DIR = "results"

QUANTIZATION_LEVELS = (16, 8, 4, 2)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--results-dir", default=DEFAULT_RESULTS_DIR)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    output_dir = Path(args.output_dir)
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    try:
        image = load_image(args.input)

        stats = operations.inspect_image(image)
        text = operations.format_inspection(stats)
        print(text)
        (results_dir / "inspect.txt").write_text(text + "\n", encoding="utf-8")

        save_image(output_dir / "copy.png", operations.copy_image(image))
        for channel in ("b", "g", "r"):
            save_image(
                output_dir / ("channel_" + channel + ".png"),
                operations.extract_channel(image, channel),
            )

        average = operations.grayscale_average(image)
        weighted = operations.grayscale_weighted(image)
        save_image(output_dir / "gray_average.png", average)
        save_image(output_dir / "gray_weighted.png", weighted)

        for levels in QUANTIZATION_LEVELS:
            save_image(
                output_dir / ("quant_" + str(levels) + ".png"),
                operations.quantize(weighted, levels),
            )
    except PdiLabError as error:
        print("erro: " + str(error), file=sys.stderr)
        return 1

    print("saidas geradas em: " + str(output_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
