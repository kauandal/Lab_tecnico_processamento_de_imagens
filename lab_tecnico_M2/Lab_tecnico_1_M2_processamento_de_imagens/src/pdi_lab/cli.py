"""Linha de comando do laboratorio M2.1.

    python -m pdi_lab --input <imagem> --output <mascara.png> --operation segment --method <metodo>

Codigo de saida 0 quando deu certo, 1 em erro previsto e 2 em erro de argumento (argparse).
"""

import argparse
import sys
from pathlib import Path

import cv2 as cv

from . import __version__, segmentation
from .errors import PdiLabError
from .image_io import load_image, require_lossless, save_image


def build_parser():
    parser = argparse.ArgumentParser(
        prog="pdi_lab",
        description="Laboratorio M2.1: mascara binaria e segmentacao. A mascara usa 255 para objeto e 0 para fundo.",
    )
    parser.add_argument("--input", required=True, help="caminho da imagem de entrada")
    parser.add_argument("--output", required=True, help="arquivo da mascara (PNG, BMP ou TIFF)")
    parser.add_argument("--operation", required=True, choices=["segment"], help="operacao a executar")
    parser.add_argument("--method", required=True, choices=segmentation.METHODS, help="metodo de segmentacao")
    parser.add_argument("--threshold", type=int,
                        help="limiar do metodo fixed, de 0 a 255; objeto onde cinza > limiar")
    parser.add_argument("--block-size", type=int, default=31,
                        help="lado da vizinhanca do metodo adaptive, impar >= 3 (padrao 31)")
    parser.add_argument("--c", type=float,
                        help="constante do metodo adaptive, obrigatoria: objeto onde pixel > media local - C")
    parser.add_argument("--adaptive-kind", choices=segmentation.ADAPTIVE_KINDS, default="gaussian",
                        help="media local do metodo adaptive (padrao gaussian)")
    parser.add_argument("--hsv-lower", help="limite inferior H,S,V do metodo hsv (H 0-179, S e V 0-255)")
    parser.add_argument("--hsv-upper",
                        help="limite superior H,S,V do metodo hsv; H menor que o inferior indica faixa que cruza 179/0")
    parser.add_argument("--blur", type=int, default=0,
                        help="suavizacao gaussiana NxN antes do metodo; 0 desliga (padrao)")
    parser.add_argument("--invert", action="store_true", help="inverte a mascara, para objeto mais escuro que o fundo")
    parser.add_argument("--overlay", help="grava a imagem original com a mascara sobreposta neste caminho")
    parser.add_argument("--version", action="version", version="pdi_lab " + __version__)
    return parser


def run_segment(args):
    # o contrato pede a mascara exatamente no caminho de --output
    output = Path(args.output)
    require_lossless(output)
    if output.is_dir():
        raise PdiLabError("--output deve ser um arquivo, e nao um diretorio: " + str(output))

    hsv_lower = None
    hsv_upper = None
    if args.method == "hsv":
        if not args.hsv_lower or not args.hsv_upper:
            raise PdiLabError("o metodo hsv exige --hsv-lower e --hsv-upper")
        hsv_lower = segmentation.parse_hsv(args.hsv_lower, "--hsv-lower")
        hsv_upper = segmentation.parse_hsv(args.hsv_upper, "--hsv-upper")

    image = load_image(args.input)
    mask, info = segmentation.segment(
        image, args.method, threshold=args.threshold, block_size=args.block_size, c=args.c,
        adaptive_kind=args.adaptive_kind, hsv_lower=hsv_lower, hsv_upper=hsv_upper,
        blur=args.blur, invert=args.invert,
    )

    shape = image.shape[:2]
    segmentation.validate_mask(mask, shape)
    save_image(output, mask)

    # le de novo o arquivo gravado para conferir que ele continua binario
    saved = cv.imread(str(output), cv.IMREAD_UNCHANGED)
    if saved is None:
        raise PdiLabError("falha ao reler a mascara gravada: " + str(output))
    segmentation.validate_mask(saved, shape)

    stats = segmentation.mask_stats(saved)
    for key in info:
        print(key + "=" + str(info[key]))
    print("width=" + str(shape[1]))
    print("height=" + str(shape[0]))
    print("foreground=" + str(stats["foreground"]))
    print("foreground_ratio=%.6f" % stats["foreground_ratio"])
    print("binary_check=ok")
    print("saida gravada em: " + str(output))

    if args.overlay:
        save_image(args.overlay, segmentation.overlay(image, saved))
        print("sobreposicao gravada em: " + str(args.overlay))
    return 0


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return run_segment(args)
    except PdiLabError as error:
        print("erro: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
