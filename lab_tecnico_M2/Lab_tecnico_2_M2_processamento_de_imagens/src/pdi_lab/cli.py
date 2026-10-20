"""Interface de linha de comando dos laboratórios M2.1 e M2.2.

Forma geral de uso::

    python -m pdi_lab --input <imagem> --output <mascara.png> \
        --operation segment --method fixed|otsu|adaptive|hsv [parametros]

    python -m pdi_lab --input <mascara.png> --output <prefixo> \
        --operation analyze --sequence <config.json> [--connectivity 4|8] \
        [--min-area N]

Códigos de saída:

* ``0`` operação concluída;
* ``1`` erro previsto de execução, com mensagem explicativa;
* ``2`` erro de uso dos argumentos, tratado pelo ``argparse``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2 as cv

from . import __version__, analysis, segmentation
from .errors import PdiLabError
from .image_io import load_image, require_lossless, save_image

EXIT_SUCCESS = 0
EXIT_ERROR = 1

OPERATIONS = ("segment", "analyze")


def build_parser() -> argparse.ArgumentParser:
    """Monta o analisador de argumentos da aplicação."""
    parser = argparse.ArgumentParser(
        prog="pdi_lab",
        description=(
            "Laboratorios M2.1 e M2.2: segmentacao, componentes conexos e "
            "morfologia. A mascara usa 255 para objeto e 0 para fundo."
        ),
    )
    parser.add_argument(
        "--input",
        required=True,
        help="imagem de entrada; em analyze, a mascara binaria",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="em segment, arquivo da mascara ou diretorio; em analyze, "
        "prefixo dos arquivos gerados",
    )
    parser.add_argument(
        "--operation", required=True, choices=OPERATIONS, help="operacao a executar"
    )
    parser.add_argument(
        "--method",
        choices=segmentation.METHODS,
        help="metodo de segmentacao, obrigatorio em segment",
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
        "--connectivity",
        type=int,
        choices=analysis.CONNECTIVITIES,
        default=8,
        help="conectividade da analise final em analyze (padrao 8)",
    )
    parser.add_argument(
        "--min-area",
        type=int,
        default=0,
        help="area minima, em pixels, para manter um componente (padrao 0)",
    )
    parser.add_argument(
        "--sequence",
        help="arquivo JSON com a sequencia morfologica, obrigatorio em analyze",
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
    if not args.method:
        raise PdiLabError("a operacao segment exige --method")
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


def run_analyze(args: argparse.Namespace) -> int:
    """Rotula a máscara, aplica a sequência morfológica e rotula de novo."""
    if not args.sequence:
        raise PdiLabError("a operacao analyze exige --sequence")
    steps = analysis.load_sequence(args.sequence)
    if args.min_area < 0:
        raise PdiLabError(
            "--min-area deve ser inteiro nao negativo, recebido: " + str(args.min_area)
        )

    initial = analysis.require_binary_mask(load_image(args.input))
    prefix = str(args.output)

    # Cópia da máscara inicial, para comparar com os estágios.
    save_image(prefix + "_initial_mask.png", initial)

    # A mesma máscara inicial é rotulada nas duas conectividades.
    initial_counts = {}
    for connectivity in analysis.CONNECTIVITIES:
        _, rows = analysis.label_components(initial, connectivity)
        initial_counts[connectivity] = len(rows)
    _, initial_rows = analysis.label_components(initial, args.connectivity)
    analysis.apply_min_area(initial_rows, args.min_area)
    analysis.write_components_csv(prefix + "_initial.csv", initial_rows)

    current = initial
    stage_files = []
    stage_counts = []
    for index, step in enumerate(steps, start=1):
        current = analysis.apply_step(current, step)
        stage = prefix + "_stage_" + str(index) + "_" + step.operation + ".png"
        save_image(stage, current)
        stage_files.append(Path(stage).as_posix())

        # Contagem após cada estágio, para ver o efeito de cada operação.
        _, rows = analysis.label_components(current, args.connectivity)
        analysis.apply_min_area(rows, args.min_area)
        stage_counts.append(analysis.count_summary(rows))
        print(
            "estagio {0}: {1} -> {2} (brutos={3} filtrados={4} area={5})".format(
                index,
                step.describe(),
                stage,
                stage_counts[-1]["count_raw"],
                stage_counts[-1]["count_kept"],
                stage_counts[-1]["area_raw"],
            )
        )

    final = current
    save_image(prefix + "_final_mask.png", final)
    final_counts = {}
    for connectivity in analysis.CONNECTIVITIES:
        _, rows = analysis.label_components(final, connectivity)
        final_counts[connectivity] = len(rows)
    final_labels, final_rows = analysis.label_components(final, args.connectivity)
    analysis.apply_min_area(final_rows, args.min_area)
    analysis.write_components_csv(prefix + "_final.csv", final_rows)
    save_image(prefix + "_labels.png", analysis.labels_image(final_labels, final_rows))

    before = analysis.count_summary(initial_rows)
    after = analysis.count_summary(final_rows)
    summary = {
        "input": Path(args.input).as_posix(),
        "connectivity": args.connectivity,
        "min_area": args.min_area,
        "sequence": [step.as_dict() for step in steps],
        "stages": stage_files,
        "stage_counts": stage_counts,
        "initial": {
            "foreground": int((initial == segmentation.FOREGROUND).sum()),
            "count_4": initial_counts[4],
            "count_8": initial_counts[8],
            **before,
        },
        "final": {
            "foreground": int((final == segmentation.FOREGROUND).sum()),
            "count_4": final_counts[4],
            "count_8": final_counts[8],
            **after,
        },
    }
    summary_path = Path(prefix + "_summary.json")
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print("conectividade=" + str(args.connectivity))
    print("min_area=" + str(args.min_area))
    for name, counts, totals in (
        ("inicial", initial_counts, before),
        ("final", final_counts, after),
    ):
        print(
            "{0}: componentes_4={1} componentes_8={2} brutos={3} filtrados={4} "
            "area={5}".format(
                name,
                counts[4],
                counts[8],
                totals["count_raw"],
                totals["count_kept"],
                totals["area_raw"],
            )
        )
    print("resumo gravado em: " + str(summary_path))
    return EXIT_SUCCESS


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada da linha de comando."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.operation == "analyze":
            return run_analyze(args)
        return run_segment(args)
    except PdiLabError as error:
        print("erro: " + str(error), file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
