"""Linha de comando dos laboratorios M2.1 e M2.2.

    python -m pdi_lab --input <imagem> --output <mascara.png> --operation segment --method <metodo>
    python -m pdi_lab --input <mascara.png> --output <prefixo> --operation analyze --sequence <config.json>

Codigo de saida 0 quando deu certo, 1 em erro previsto e 2 em erro de argumento (argparse).
"""

import argparse
import json
import sys
from pathlib import Path

import cv2 as cv

from . import __version__, analysis, segmentation
from .errors import PdiLabError
from .image_io import load_image, require_lossless, save_image


def build_parser():
    parser = argparse.ArgumentParser(
        prog="pdi_lab",
        description="Laboratorios M2.1 e M2.2: segmentacao, componentes conexos e morfologia. "
                    "A mascara usa 255 para objeto e 0 para fundo.",
    )
    parser.add_argument("--input", required=True, help="imagem de entrada; em analyze, a mascara binaria")
    parser.add_argument("--output", required=True,
                        help="em segment, arquivo da mascara (PNG, BMP ou TIFF); em analyze, "
                             "prefixo dos arquivos gerados")
    parser.add_argument("--operation", required=True, choices=["segment", "analyze"], help="operacao a executar")

    # parametros do segment
    parser.add_argument("--method", choices=segmentation.METHODS, help="metodo de segmentacao, obrigatorio em segment")
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

    # parametros do analyze
    parser.add_argument("--connectivity", type=int, choices=analysis.CONNECTIVITIES, default=8,
                        help="conectividade da analise final em analyze (padrao 8)")
    parser.add_argument("--min-area", type=int, default=0,
                        help="area minima, em pixels, para manter um componente (padrao 0)")
    parser.add_argument("--sequence", help="arquivo JSON com a sequencia morfologica, obrigatorio em analyze")

    parser.add_argument("--version", action="version", version="pdi_lab " + __version__)
    return parser


def run_segment(args):
    if not args.method:
        raise PdiLabError("a operacao segment exige --method")

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


def run_analyze(args):
    if not args.sequence:
        raise PdiLabError("a operacao analyze exige --sequence")
    steps = analysis.load_sequence(args.sequence)
    if args.min_area < 0:
        raise PdiLabError("--min-area deve ser inteiro nao negativo, recebido: " + str(args.min_area))

    initial = analysis.require_binary_mask(load_image(args.input))
    prefix = str(args.output)

    # copia da mascara inicial
    save_image(prefix + "_initial_mask.png", initial)

    # mesma mascara contada com conectividade 4 e 8
    _, rows4 = analysis.label_components(initial, 4)
    _, rows8 = analysis.label_components(initial, 8)
    initial_count_4 = len(rows4)
    initial_count_8 = len(rows8)

    _, initial_rows = analysis.label_components(initial, args.connectivity)
    analysis.apply_min_area(initial_rows, args.min_area)
    analysis.write_components_csv(prefix + "_initial.csv", initial_rows)

    # sequencia morfologica, salvando cada estagio
    mask = initial
    stage_files = []
    stage_counts = []
    n = 0
    for step in steps:
        n += 1
        mask = analysis.apply_step(mask, step)
        stage = prefix + "_stage_" + str(n) + "_" + step["operation"] + ".png"
        save_image(stage, mask)
        stage_files.append(Path(stage).as_posix())

        _, rows = analysis.label_components(mask, args.connectivity)
        analysis.apply_min_area(rows, args.min_area)
        counts = analysis.count_summary(rows)
        stage_counts.append(counts)
        print("estagio {}: {} -> {} (brutos={} filtrados={} area={})".format(
            n, analysis.step_text(step), stage, counts["count_raw"], counts["count_kept"], counts["area_raw"]))

    final = mask
    save_image(prefix + "_final_mask.png", final)
    _, rows4 = analysis.label_components(final, 4)
    _, rows8 = analysis.label_components(final, 8)
    final_count_4 = len(rows4)
    final_count_8 = len(rows8)

    final_labels, final_rows = analysis.label_components(final, args.connectivity)
    analysis.apply_min_area(final_rows, args.min_area)
    analysis.write_components_csv(prefix + "_final.csv", final_rows)
    save_image(prefix + "_labels.png", analysis.labels_image(final_labels, final_rows))

    before = analysis.count_summary(initial_rows)
    after = analysis.count_summary(final_rows)

    initial_info = {"foreground": int((initial == 255).sum()), "count_4": initial_count_4, "count_8": initial_count_8}
    initial_info.update(before)
    final_info = {"foreground": int((final == 255).sum()), "count_4": final_count_4, "count_8": final_count_8}
    final_info.update(after)

    summary = {
        "input": Path(args.input).as_posix(),
        "connectivity": args.connectivity,
        "min_area": args.min_area,
        "sequence": steps,
        "stages": stage_files,
        "stage_counts": stage_counts,
        "initial": initial_info,
        "final": final_info,
    }
    summary_path = Path(prefix + "_summary.json")
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("conectividade=" + str(args.connectivity))
    print("min_area=" + str(args.min_area))
    print("inicial: componentes_4={} componentes_8={} brutos={} filtrados={} area={}".format(
        initial_count_4, initial_count_8, before["count_raw"], before["count_kept"], before["area_raw"]))
    print("final: componentes_4={} componentes_8={} brutos={} filtrados={} area={}".format(
        final_count_4, final_count_8, after["count_raw"], after["count_kept"], after["area_raw"]))
    print("resumo gravado em: " + str(summary_path))
    return 0


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.operation == "analyze":
            return run_analyze(args)
        return run_segment(args)
    except PdiLabError as error:
        print("erro: " + str(error), file=sys.stderr)
        return 1
    except OSError as error:
        # erro ao gravar CSV ou JSON
        print("erro: falha de leitura ou gravacao: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
