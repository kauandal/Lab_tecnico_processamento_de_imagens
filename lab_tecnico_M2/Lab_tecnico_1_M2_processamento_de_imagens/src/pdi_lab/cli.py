"""Interface de linha de comando do laboratório M2.1.

Forma geral de uso::

    python -m pdi_lab --input <imagem> --output <mascara.png> \
        --operation segment --method fixed|otsu|adaptive|hsv [parametros]

Códigos de saída:

* ``0`` operação concluída e máscara validada;
* ``1`` erro previsto de execução, com mensagem explicativa;
* ``2`` erro de uso dos argumentos, tratado pelo ``argparse``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2 as cv

from . import __version__, segmentation
from .errors import PdiLabError
from .image_io import load_image, require_lossless, save_image

EXIT_SUCCESS = 0
EXIT_ERROR = 1

OPERATIONS = ("segment",)


def build_parser() -> argparse.ArgumentParser:
    """Monta o analisador de argumentos da aplicação."""
    parser = argparse.ArgumentParser(
        prog="pdi_lab",
        description=(
            "Laboratorio M2.1: mascara binaria e segmentacao. A mascara usa "
            "255 para objeto e 0 para fundo."
        ),
    )
    parser.add_argument("--input", required=True, help="caminho da imagem de entrada")
    parser.add_argument(
        "--output",
        required=True,
        help="arquivo da mascara (PNG, BMP ou TIFF) ou diretorio de saida",
    )
    parser.add_argument(
        "--operation", required=True, choices=OPERATIONS, help="operacao a executar"
    )
    parser.add_argument(
        "--method",
        required=True,
        choices=segmentation.METHODS,
        help="metodo de segmentacao",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        help="limiar do metodo fixed, de 0 a 255; objeto onde cinza > limiar",
    )
    parser.add_argument(
        "--block-size",
        type=int,
        default=31,
        help="lado da vizinhanca do metodo adaptive, impar >= 3 (padrao 31)",
    )
    parser.add_argument(
        "--c",
        type=float,
        help="constante do metodo adaptive, obrigatoria: objeto onde pixel > "
        "media local - C; C negativo exige contraste acima da media",
    )
    parser.add_argument(
        "--adaptive-kind",
        choices=segmentation.ADAPTIVE_KINDS,
        default=segmentation.ADAPTIVE_GAUSSIAN,
        help="media local do metodo adaptive (padrao gaussian)",
    )
    parser.add_argument(
        "--hsv-lower",
        help="limite inferior H,S,V do metodo hsv (H 0-179, S e V 0-255)",
    )
    parser.add_argument(
        "--hsv-upper",
        help="limite superior H,S,V do metodo hsv; H menor que o inferior "
        "indica faixa que cruza 179/0",
    )
    parser.add_argument(
        "--blur",
        type=int,
        default=0,
        help="pre-processamento gaussiano NxN antes do metodo; 0 desliga (padrao)",
    )
    parser.add_argument(
        "--invert",
        action="store_true",
        help="inverte a mascara, para objetos mais escuros que o fundo",
    )
    parser.add_argument(
        "--overlay",
        help="grava a imagem original com a mascara sobreposta neste caminho",
    )
    parser.add_argument(
        "--version", action="version", version="pdi_lab " + __version__
    )
    return parser


def default_name(args: argparse.Namespace) -> str:
    """Nome de arquivo usado quando --output aponta para um diretório."""
    return Path(args.input).stem + "_mask_" + args.method + ".png"


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


def run_segment(args: argparse.Namespace) -> int:
    """Gera, grava e valida a máscara; opcionalmente grava a sobreposição."""
    output = resolve_output_path(args.output, args)
    require_lossless(output)

    hsv_lower = hsv_upper = None
    if args.method == segmentation.METHOD_HSV:
        if not args.hsv_lower or not args.hsv_upper:
            raise PdiLabError("o metodo hsv exige --hsv-lower e --hsv-upper")
        hsv_lower = segmentation.parse_hsv(args.hsv_lower, "--hsv-lower")
        hsv_upper = segmentation.parse_hsv(args.hsv_upper, "--hsv-upper")

    image = load_image(args.input)
    result = segmentation.segment(
        image,
        args.method,
        threshold=args.threshold,
        block_size=args.block_size,
        c=args.c,
        adaptive_kind=args.adaptive_kind,
        hsv_lower=hsv_lower,
        hsv_upper=hsv_upper,
        blur=args.blur,
        invert=args.invert,
    )

    expected_shape = image.shape[:2]
    segmentation.validate_mask(result.mask, expected_shape)
    save_image(output, result.mask)

    # Relê o arquivo gravado para garantir que a máscara persistida, e não só a
    # matriz em memória, continua binária e com as dimensões da entrada.
    persisted = cv.imread(str(output), cv.IMREAD_UNCHANGED)
    if persisted is None:
        raise PdiLabError("falha ao reler a mascara gravada: " + str(output))
    segmentation.validate_mask(persisted, expected_shape)

    stats = segmentation.mask_stats(persisted)
    for key, value in result.details.items():
        print(key + "=" + str(value))
    print("width=" + str(expected_shape[1]))
    print("height=" + str(expected_shape[0]))
    print("foreground=" + str(stats["foreground"]))
    print("foreground_ratio={0:.6f}".format(stats["foreground_ratio"]))
    print("binary_check=ok")
    print("saida gravada em: " + str(output))

    if args.overlay:
        overlay_path = save_image(args.overlay, segmentation.overlay(image, persisted))
        print("sobreposicao gravada em: " + str(overlay_path))

    return EXIT_SUCCESS


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada da linha de comando."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return run_segment(args)
    except PdiLabError as error:
        print("erro: " + str(error), file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
