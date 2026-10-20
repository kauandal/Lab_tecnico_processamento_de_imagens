"""Interface de linha de comando do laboratório M1.2.

Forma geral de uso::

    python -m pdi_lab --input <arquivo> --output <arquivo-ou-diretorio> \
        --operation <operacao> [--value N] [--alpha F] [--threshold N]

Códigos de saída:

* ``0`` operação concluída;
* ``1`` erro previsto de execução, com mensagem explicativa;
* ``2`` erro de uso dos argumentos, tratado pelo ``argparse``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__, operations
from .errors import PdiLabError
from .image_io import load_image, save_image

EXIT_SUCCESS = 0
EXIT_ERROR = 1

OPERATIONS = (
    "brightness",
    "contrast",
    "negative",
    "threshold",
    "histogram",
    "grayscale_weighted",
)

# Nome usado quando --output aponta para um diretório.
DEFAULT_OUTPUT_NAME = {
    "brightness": "brightness.png",
    "contrast": "contrast.png",
    "negative": "negative.png",
    "threshold": "threshold.png",
    "histogram": "histogram.csv",
    "grayscale_weighted": "gray_weighted.png",
}


def build_parser() -> argparse.ArgumentParser:
    """Monta o analisador de argumentos da aplicação."""
    parser = argparse.ArgumentParser(
        prog="pdi_lab",
        description=(
            "Laboratorio M1.2: transformacoes de intensidade. As operacoes "
            "sao implementadas manualmente, com percurso explicito dos pixels."
        ),
    )
    parser.add_argument(
        "--input",
        required=True,
        help="caminho da imagem de entrada",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="arquivo ou diretorio de saida",
    )
    parser.add_argument(
        "--operation",
        required=True,
        choices=OPERATIONS,
        help="operacao a executar",
    )
    parser.add_argument(
        "--value",
        type=int,
        help="deslocamento de brilho, positivo clareia e negativo escurece",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        help="fator de contraste, maior ou igual a zero",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        help="limiar da binarizacao, entre 0 e 255",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="pdi_lab " + __version__,
    )
    return parser


def _format_number(value: float) -> str:
    """Formata um número para compor nome de arquivo, sem ponto decimal."""
    if float(value).is_integer():
        return str(int(value))
    return str(value).replace(".", "_").replace("-", "neg")


def resolve_output_path(output: str, args: argparse.Namespace) -> Path:
    """Resolve ``--output`` aceitando tanto arquivo quanto diretório."""
    path = Path(output)
    operation = args.operation
    looks_like_directory = (
        path.is_dir()
        or output.endswith("/")
        or output.endswith("\\")
        or path.suffix == ""
    )

    if not looks_like_directory:
        return path

    name = DEFAULT_OUTPUT_NAME[operation]
    if operation == "brightness" and args.value is not None:
        name = "brightness_" + _format_number(args.value) + ".png"
    elif operation == "contrast" and args.alpha is not None:
        name = "contrast_" + _format_number(args.alpha) + ".png"
    elif operation == "threshold" and args.threshold is not None:
        name = "threshold_" + str(args.threshold) + ".png"
    return path / name


def run(args: argparse.Namespace) -> int:
    """Executa a operação escolhida e devolve o código de saída."""
    image = load_image(args.input)
    operation = args.operation
    path = resolve_output_path(args.output, args)

    if operation == "histogram":
        counts = operations.histogram(image)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(operations.format_histogram(counts) + "\n", encoding="utf-8")
        print("saida gravada em: " + str(path))
        return EXIT_SUCCESS

    if operation == "brightness":
        if args.value is None:
            raise PdiLabError("a operacao brightness exige --value")
        result = operations.brightness(image, args.value)
    elif operation == "contrast":
        if args.alpha is None:
            raise PdiLabError("a operacao contrast exige --alpha")
        result = operations.contrast(image, args.alpha)
    elif operation == "negative":
        result = operations.negative(image)
    elif operation == "threshold":
        if args.threshold is None:
            raise PdiLabError("a operacao threshold exige --threshold")
        result = operations.threshold(image, args.threshold)
    elif operation == "grayscale_weighted":
        result = operations.to_grayscale(image)
    else:  # pragma: no cover - protegido pelas escolhas do argparse
        raise PdiLabError("operacao nao suportada: " + operation)

    save_image(path, result)
    print("saida gravada em: " + str(path))
    return EXIT_SUCCESS


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada da linha de comando."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return run(args)
    except PdiLabError as error:
        print("erro: " + str(error), file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
