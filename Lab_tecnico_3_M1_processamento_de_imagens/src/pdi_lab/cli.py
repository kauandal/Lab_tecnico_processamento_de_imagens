"""Interface de linha de comando do laboratório M1.3.

Forma geral de uso::

    python -m pdi_lab --input <arquivo> --output <arquivo-ou-diretorio> \
        --operation <operacao> [--kernel <arquivo>] [--border copy|replicate] \
        [--size N] [--view MODO] [--component gx|gy|l1|l2] [--alpha F]

Códigos de saída:

* ``0`` operação concluída;
* ``1`` erro previsto de execução, com mensagem explicativa;
* ``2`` erro de uso dos argumentos, tratado pelo ``argparse``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from . import __version__, operations
from .errors import PdiLabError
from .image_io import load_image, save_image
from .kernels import load_kernel

EXIT_SUCCESS = 0
EXIT_ERROR = 1

OPERATIONS = (
    "convolution",
    "mean_filter",
    "weighted_mean",
    "laplacian",
    "laplacian_enhance",
    "sobel",
    "grayscale_weighted",
)

SOBEL_COMPONENTS = ("gx", "gy", "l1", "l2")

# Modo de visualização adotado quando --view não é informado. As respostas com
# sinal usam o deslocamento de 128; as demais apenas saturam.
DEFAULT_VIEW = {
    "convolution": operations.VIEW_CLAMP,
    "mean_filter": operations.VIEW_CLAMP,
    "weighted_mean": operations.VIEW_CLAMP,
    "laplacian": operations.VIEW_OFFSET_NAME,
    "sobel_gx": operations.VIEW_OFFSET_NAME,
    "sobel_gy": operations.VIEW_OFFSET_NAME,
    "sobel_l1": operations.VIEW_CLAMP,
    "sobel_l2": operations.VIEW_CLAMP,
}


def build_parser() -> argparse.ArgumentParser:
    """Monta o analisador de argumentos da aplicação."""
    parser = argparse.ArgumentParser(
        prog="pdi_lab",
        description=(
            "Laboratorio M1.3: convolucao e filtragem espacial. As operacoes "
            "de vizinhanca e o tratamento de bordas sao implementados "
            "manualmente."
        ),
    )
    parser.add_argument("--input", required=True, help="caminho da imagem de entrada")
    parser.add_argument(
        "--output", required=True, help="arquivo ou diretorio de saida"
    )
    parser.add_argument(
        "--operation", required=True, choices=OPERATIONS, help="operacao a executar"
    )
    parser.add_argument(
        "--kernel",
        help="arquivo de kernel, obrigatorio para a operacao convolution",
    )
    parser.add_argument(
        "--border",
        choices=operations.BORDER_STRATEGIES,
        default=operations.BORDER_REPLICATE,
        help="estrategia de tratamento de borda",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=3,
        help="lado da janela do filtro de media, inteiro impar",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=1.0,
        help="fator multiplicativo aplicado ao kernel lido de arquivo",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=1.0,
        help="intensidade do realce Laplaciano",
    )
    parser.add_argument(
        "--component",
        choices=SOBEL_COMPONENTS,
        default="l2",
        help="componente do Sobel a gravar",
    )
    parser.add_argument(
        "--view",
        choices=operations.VIEWS,
        help="transformacao aplicada a resposta bruta para visualizacao",
    )
    parser.add_argument(
        "--raw-output",
        help="grava a resposta bruta, sem saturar, em arquivo CSV",
    )
    parser.add_argument(
        "--version", action="version", version="pdi_lab " + __version__
    )
    return parser


def default_name(args: argparse.Namespace) -> str:
    """Nome de arquivo usado quando --output aponta para um diretório."""
    operation = args.operation
    suffix = "_" + args.border

    if operation == "convolution":
        stem = Path(args.kernel).stem if args.kernel else "convolution"
        return stem + suffix + ".png"
    if operation == "mean_filter":
        return "mean_" + str(args.size) + "x" + str(args.size) + suffix + ".png"
    if operation == "weighted_mean":
        return "weighted_mean_3x3" + suffix + ".png"
    if operation == "laplacian":
        return "laplacian" + suffix + ".png"
    if operation == "laplacian_enhance":
        return "laplacian_enhance" + suffix + ".png"
    if operation == "sobel":
        return "sobel_" + args.component + suffix + ".png"
    return "gray_weighted.png"


def resolve_output_path(output: str, args: argparse.Namespace) -> Path:
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
    return path / default_name(args)


def write_raw_csv(raw: np.ndarray, path: Path) -> None:
    """Grava a resposta bruta em CSV, uma linha da imagem por linha do arquivo."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for row in raw.tolist():
        lines.append(",".join("{0:.6f}".format(value) for value in row))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def compute(args: argparse.Namespace, image: np.ndarray):
    """Executa a operação e devolve a resposta bruta e o modo de visualização.

    Para ``laplacian_enhance`` e ``grayscale_weighted`` o resultado já é uma
    imagem de 8 bits, e o modo de visualização devolvido é ``None``.
    """
    operation = args.operation

    if operation == "convolution":
        if not args.kernel:
            raise PdiLabError("a operacao convolution exige --kernel")
        kernel = load_kernel(args.kernel)
        if args.scale != 1.0:
            kernel = [[value * args.scale for value in row] for row in kernel]
        return operations.convolve(image, kernel, args.border), DEFAULT_VIEW[operation]

    if operation == "mean_filter":
        return (
            operations.mean_filter(image, args.size, args.border),
            DEFAULT_VIEW[operation],
        )

    if operation == "weighted_mean":
        return (
            operations.weighted_mean(image, args.border),
            DEFAULT_VIEW[operation],
        )

    if operation == "laplacian":
        return operations.laplacian(image, args.border), DEFAULT_VIEW[operation]

    if operation == "sobel":
        responses = operations.sobel(image, args.border)
        return (
            responses[args.component],
            DEFAULT_VIEW["sobel_" + args.component],
        )

    if operation == "laplacian_enhance":
        return (
            operations.laplacian_enhance(image, args.border, args.alpha),
            None,
        )

    if operation == "grayscale_weighted":
        return operations.to_grayscale(image), None

    # pragma: no cover - protegido pelas escolhas do argparse
    raise PdiLabError("operacao nao suportada: " + operation)


def run(args: argparse.Namespace) -> int:
    """Executa a operação escolhida e devolve o código de saída."""
    image = load_image(args.input)
    result, default_view = compute(args, image)

    if default_view is None:
        picture = result
    else:
        view = args.view or default_view
        if args.raw_output:
            write_raw_csv(result, Path(args.raw_output))
            print("resposta bruta gravada em: " + str(args.raw_output))
        picture = operations.to_uint8(result, view)
        print("visualizacao: " + view)

    path = resolve_output_path(args.output, args)
    save_image(path, picture)
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
