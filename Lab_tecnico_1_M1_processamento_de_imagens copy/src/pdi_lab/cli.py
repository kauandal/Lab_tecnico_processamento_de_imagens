"""Interface de linha de comando do laboratório M1.1.

Forma geral de uso::

    python -m pdi_lab --input <arquivo> --output <arquivo-ou-diretorio> \
        --operation <operacao> [--levels N]

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
    "inspect",
    "copy",
    "channel_b",
    "channel_g",
    "channel_r",
    "grayscale_average",
    "grayscale_weighted",
    "quantize",
)

# Nome usado quando --output aponta para um diretório.
DEFAULT_OUTPUT_NAME = {
    "inspect": "inspect.txt",
    "copy": "copy.png",
    "channel_b": "channel_b.png",
    "channel_g": "channel_g.png",
    "channel_r": "channel_r.png",
    "grayscale_average": "gray_average.png",
    "grayscale_weighted": "gray_weighted.png",
    "quantize": "quant.png",
}


def build_parser() -> argparse.ArgumentParser:
    """Monta o analisador de argumentos da aplicação."""
    parser = argparse.ArgumentParser(
        prog="pdi_lab",
        description=(
            "Laboratorio M1.1: representacao, canais e niveis de cinza. "
            "As operacoes sao implementadas manualmente, com percurso "
            "explicito dos pixels."
        ),
    )
    parser.add_argument(
        "--input",
        required=True,
        help="caminho da imagem de entrada",
    )
    parser.add_argument(
        "--output",
        help=(
            "arquivo ou diretorio de saida; opcional apenas para a operacao "
            "inspect, que sempre escreve na saida padrao"
        ),
    )
    parser.add_argument(
        "--operation",
        required=True,
        choices=OPERATIONS,
        help="operacao a executar",
    )
    parser.add_argument(
        "--levels",
        type=int,
        help="quantidade de niveis da quantizacao, entre 2 e 256",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="pdi_lab " + __version__,
    )
    return parser


def resolve_output_path(output: str, operation: str, levels: int | None) -> Path:
    """Resolve ``--output`` aceitando tanto arquivo quanto diretório."""
    path = Path(output)
    looks_like_directory = (
        path.is_dir()
        or output.endswith("/")
        or output.endswith("\\")
        or path.suffix == ""
    )

    if not looks_like_directory:
        return path

    name = DEFAULT_OUTPUT_NAME[operation]
    if operation == "quantize" and levels is not None:
        name = "quant_" + str(levels) + ".png"
    return path / name


def run(args: argparse.Namespace) -> int:
    """Executa a operação escolhida e devolve o código de saída."""
    image = load_image(args.input)
    operation = args.operation

    if operation == "inspect":
        text = operations.format_inspection(operations.inspect_image(image))
        print(text)
        if args.output:
            path = resolve_output_path(args.output, operation, args.levels)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text + "\n", encoding="utf-8")
            print("saida gravada em: " + str(path))
        return EXIT_SUCCESS

    if not args.output:
        raise PdiLabError(
            "a operacao " + operation + " exige --output"
        )

    if operation == "copy":
        result = operations.copy_image(image)
    elif operation.startswith("channel_"):
        result = operations.extract_channel(image, operation.split("_")[1])
    elif operation == "grayscale_average":
        result = operations.grayscale_average(image)
    elif operation == "grayscale_weighted":
        result = operations.grayscale_weighted(image)
    elif operation == "quantize":
        if args.levels is None:
            raise PdiLabError("a operacao quantize exige --levels")
        result = operations.quantize(image, args.levels)
    else:  # pragma: no cover - protegido pelas escolhas do argparse
        raise PdiLabError("operacao nao suportada: " + operation)

    path = resolve_output_path(args.output, operation, args.levels)
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
