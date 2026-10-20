"""Testes de componentes conexos, sequência morfológica e operação analyze."""

import csv
import json
from pathlib import Path

import cv2 as cv
import numpy as np
import pytest

from pdi_lab import analysis
from pdi_lab.analysis import Step
from pdi_lab.cli import main
from pdi_lab.errors import PdiLabError

PROJECT = Path(__file__).resolve().parent.parent
SEQUENCE = PROJECT / "config" / "coins.json"


def open_step(size=3):
    return Step("open", "ellipse", size, 1, "remover ruido")


def close_step(size=3):
    return Step("close", "ellipse", size, 1, "fechar furo")


def write_mask(tmp_path, mask, name="mask.png"):
    path = tmp_path / name
    cv.imwrite(str(path), mask)
    return path


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def analyze_args(mask_path, prefix, *extra):
    return [
        "--input",
        str(mask_path),
        "--output",
        str(prefix),
        "--operation",
        "analyze",
        "--sequence",
        str(SEQUENCE),
        *extra,
    ]


# --- conectividade -------------------------------------------------------


def test_dois_pixels_na_diagonal():
    """Dois pixels só se tocam pelo canto: 2 componentes em 4 e 1 em 8."""
    mask = np.zeros((4, 4), dtype=np.uint8)
    mask[1, 1] = 255
    mask[2, 2] = 255

    _, rows4 = analysis.label_components(mask, 4)
    _, rows8 = analysis.label_components(mask, 8)

    assert len(rows4) == 2
    assert len(rows8) == 1
    assert rows8[0]["area"] == 2


def test_estatisticas_do_componente():
    mask = np.zeros((10, 12), dtype=np.uint8)
    mask[2:5, 3:7] = 255

    _, rows = analysis.label_components(mask, 8)

    assert len(rows) == 1
    row = rows[0]
    assert row["area"] == 12
    assert (row["x"], row["y"], row["width"], row["height"]) == (3, 2, 4, 3)
    assert row["cx"] == pytest.approx(4.5)
    assert row["cy"] == pytest.approx(3.0)


def test_mascara_vazia_tem_zero_componentes():
    mask = np.zeros((5, 5), dtype=np.uint8)

    for connectivity in (4, 8):
        _, rows = analysis.label_components(mask, connectivity)
        assert rows == []


def test_objeto_que_toca_a_borda():
    mask = np.zeros((6, 6), dtype=np.uint8)
    mask[0:3, 0:2] = 255

    _, rows = analysis.label_components(mask, 8)
    opened = analysis.apply_step(mask, Step("open", "rect", 3, 1, "teste"))

    assert len(rows) == 1
    assert (rows[0]["x"], rows[0]["y"]) == (0, 0)
    assert rows[0]["area"] == 6
    assert np.count_nonzero(opened) > 0, "a borda da imagem nao deve apagar o objeto"


def test_conectividade_invalida_na_funcao():
    with pytest.raises(PdiLabError):
        analysis.label_components(np.zeros((3, 3), dtype=np.uint8), 6)


# --- morfologia ----------------------------------------------------------


def test_abertura_remove_ruido_isolado_e_mantem_a_regiao():
    mask = np.zeros((20, 20), dtype=np.uint8)
    mask[5:15, 5:15] = 255
    mask[1, 18] = 255
    mask[18, 1] = 255

    opened = analysis.apply_step(mask, open_step(3))
    _, rows = analysis.label_components(opened, 8)

    assert opened[1, 18] == 0 and opened[18, 1] == 0
    assert len(rows) == 1
    assert opened[10, 10] == 255


def test_fechamento_preenche_furo_pequeno():
    mask = np.zeros((20, 20), dtype=np.uint8)
    mask[5:15, 5:15] = 255
    mask[9:11, 9:11] = 0

    closed = analysis.apply_step(mask, close_step(5))

    assert np.all(closed[9:11, 9:11] == 255)
    assert np.array_equal(closed[5:15, 5:15], np.full((10, 10), 255, dtype=np.uint8))


def test_fechamento_grande_junta_regioes_vizinhas():
    """Efeito indesejado: elemento maior que o espaço entre objetos os funde."""
    mask = np.zeros((20, 30), dtype=np.uint8)
    mask[5:15, 3:12] = 255
    mask[5:15, 15:24] = 255

    _, before = analysis.label_components(mask, 8)
    _, after = analysis.label_components(analysis.apply_step(mask, close_step(7)), 8)

    assert len(before) == 2
    assert len(after) == 1


# --- configuração da sequência -------------------------------------------


def step_dict(**changes):
    data = {
        "operation": "open",
        "shape": "ellipse",
        "size": 3,
        "iterations": 1,
        "purpose": "remover ruido",
    }
    data.update(changes)
    return data


def test_sequencia_valida():
    steps = analysis.parse_steps(
        {"steps": [step_dict(), step_dict(operation="close", size=7)]}
    )

    assert [step.operation for step in steps] == ["open", "close"]
    assert steps[1].size == 7


@pytest.mark.parametrize(
    "steps",
    [
        [step_dict()],
        [step_dict(operation="erode"), step_dict(operation="dilate")],
        [step_dict(), step_dict()],
        [step_dict(), step_dict(operation="close", size=4)],
        [step_dict(), step_dict(operation="close", size=1)],
        [step_dict(), step_dict(operation="close", iterations=0)],
        [step_dict(), step_dict(operation="close", purpose="")],
        [step_dict(), step_dict(operation="thin")],
        [step_dict(), step_dict(operation="close", shape="disk")],
    ],
    ids=[
        "um_passo",
        "sem_abertura_nem_fechamento",
        "passos_identicos_seguidos",
        "tamanho_par",
        "tamanho_1",
        "zero_iteracoes",
        "sem_finalidade",
        "operacao_desconhecida",
        "forma_desconhecida",
    ],
)
def test_sequencia_invalida(steps):
    with pytest.raises(PdiLabError):
        analysis.parse_steps({"steps": steps})


def test_arquivo_de_sequencia_inexistente_ou_invalido(tmp_path):
    with pytest.raises(PdiLabError):
        analysis.load_sequence(tmp_path / "nao_existe.json")

    broken = tmp_path / "quebrado.json"
    broken.write_text("{ steps: [", encoding="utf-8")
    with pytest.raises(PdiLabError):
        analysis.load_sequence(broken)


def test_sequencias_do_projeto_sao_validas():
    for path in (PROJECT / "config").glob("*.json"):
        assert len(analysis.load_sequence(path)) >= 2


# --- filtro por área -----------------------------------------------------


def test_filtro_por_area():
    rows = [{"area": 5}, {"area": 20}, {"area": 21}]

    analysis.apply_min_area(rows, 20)
    summary = analysis.count_summary(rows)

    assert [row["kept"] for row in rows] == [False, True, True]
    assert summary == {"count_raw": 3, "count_kept": 2, "area_raw": 46, "area_kept": 41}


def test_filtro_por_area_negativa():
    with pytest.raises(PdiLabError):
        analysis.apply_min_area([], -1)


# --- linha de comando ----------------------------------------------------


@pytest.fixture
def noisy_mask(tmp_path):
    """Dois quadrados, um com furo, e três pixels de ruído isolado."""
    mask = np.zeros((40, 40), dtype=np.uint8)
    mask[5:17, 5:17] = 255
    mask[10:12, 10:12] = 0
    mask[22:34, 22:34] = 255
    mask[2, 37] = 255
    mask[37, 2] = 255
    mask[20, 38] = 255
    return write_mask(tmp_path, mask)


def test_analyze_gera_todos_os_arquivos(tmp_path, noisy_mask):
    prefix = tmp_path / "res" / "cena"

    code = main(analyze_args(noisy_mask, prefix, "--min-area", "20"))

    assert code == 0
    for suffix in (
        "_initial_mask.png",
        "_initial.csv",
        "_stage_1_open.png",
        "_stage_2_close.png",
        "_final_mask.png",
        "_final.csv",
        "_labels.png",
        "_summary.json",
    ):
        assert (tmp_path / "res" / ("cena" + suffix)).exists(), suffix

    initial = read_csv(str(prefix) + "_initial.csv")
    final = read_csv(str(prefix) + "_final.csv")
    assert list(initial[0].keys()) == analysis.CSV_HEADER
    assert len(initial) == 5
    assert sum(row["kept"] == "true" for row in initial) == 2
    assert len(final) == 2
    assert all(row["kept"] == "true" for row in final)

    summary = json.loads((tmp_path / "res" / "cena_summary.json").read_text(encoding="utf-8"))
    assert summary["connectivity"] == 8
    assert summary["min_area"] == 20
    assert [step["operation"] for step in summary["sequence"]] == ["open", "close"]
    assert summary["initial"]["count_raw"] == 5
    assert summary["initial"]["count_kept"] == 2
    assert summary["final"]["count_raw"] == 2


def test_soma_das_areas_brutas_igual_ao_primeiro_plano(tmp_path, noisy_mask):
    prefix = tmp_path / "cena"

    assert main(analyze_args(noisy_mask, prefix)) == 0

    mask = cv.imread(str(noisy_mask), cv.IMREAD_UNCHANGED)
    initial = read_csv(str(prefix) + "_initial.csv")
    assert sum(int(row["area"]) for row in initial) == np.count_nonzero(mask)

    final_mask = cv.imread(str(prefix) + "_final_mask.png", cv.IMREAD_UNCHANGED)
    final = read_csv(str(prefix) + "_final.csv")
    assert sum(int(row["area"]) for row in final) == np.count_nonzero(final_mask)


def test_analyze_com_mascara_vazia(tmp_path):
    path = write_mask(tmp_path, np.zeros((10, 10), dtype=np.uint8))
    prefix = tmp_path / "vazia"

    code = main(analyze_args(path, prefix))

    assert code == 0
    assert read_csv(str(prefix) + "_initial.csv") == []
    assert read_csv(str(prefix) + "_final.csv") == []
    summary = json.loads(Path(str(prefix) + "_summary.json").read_text(encoding="utf-8"))
    assert summary["initial"]["count_raw"] == 0
    assert summary["final"]["count_4"] == 0


def test_analyze_conta_4_e_8_na_mesma_mascara(tmp_path, capsys):
    mask = np.zeros((6, 6), dtype=np.uint8)
    mask[1, 1] = 255
    mask[2, 2] = 255
    path = write_mask(tmp_path, mask)

    assert main(analyze_args(path, tmp_path / "diag")) == 0

    assert "inicial: componentes_4=2 componentes_8=1" in capsys.readouterr().out


@pytest.mark.parametrize("value", ["6", "0", "abc"])
def test_conectividade_invalida(tmp_path, noisy_mask, value):
    with pytest.raises(SystemExit) as excinfo:
        main(analyze_args(noisy_mask, tmp_path / "cena", "--connectivity", value))

    assert excinfo.value.code != 0


def test_area_minima_negativa(tmp_path, noisy_mask):
    code = main(analyze_args(noisy_mask, tmp_path / "cena", "--min-area", "-1"))

    assert code == 1


def test_analyze_sem_sequencia(tmp_path, noisy_mask):
    code = main(
        [
            "--input",
            str(noisy_mask),
            "--output",
            str(tmp_path / "cena"),
            "--operation",
            "analyze",
        ]
    )

    assert code == 1


def test_analyze_recusa_mascara_nao_binaria(tmp_path):
    mask = np.zeros((5, 5), dtype=np.uint8)
    mask[2, 2] = 128
    path = write_mask(tmp_path, mask)

    assert main(analyze_args(path, tmp_path / "cena")) == 1


def test_analyze_recusa_imagem_colorida(tmp_path):
    path = write_mask(tmp_path, np.zeros((5, 5, 3), dtype=np.uint8))

    assert main(analyze_args(path, tmp_path / "cena")) == 1


def test_imagem_de_rotulos(tmp_path):
    mask = np.zeros((20, 20), dtype=np.uint8)
    mask[2:8, 2:8] = 255
    mask[15, 15] = 255
    labels, rows = analysis.label_components(mask, 8)
    analysis.apply_min_area(rows, 5)

    image = analysis.labels_image(labels, rows)

    assert image.shape == (20, 20, 3)
    assert tuple(image[0, 0]) == (0, 0, 0)
    assert tuple(image[1, 1]) == (0, 0, 0)
    assert tuple(image[2, 2]) == analysis.BOX_KEPT, "canto da caixa do componente mantido"


def test_analyze_mascara_inexistente(tmp_path, capsys):
    code = main(analyze_args(tmp_path / "nao_existe.png", tmp_path / "cena"))

    assert code == 1
    assert "erro:" in capsys.readouterr().err


def test_analyze_falha_de_gravacao(tmp_path, noisy_mask, capsys):
    """O prefixo aponta para dentro de um arquivo, então a gravação falha."""
    bloqueio = tmp_path / "arquivo.txt"
    bloqueio.write_text("x", encoding="utf-8")

    code = main(analyze_args(noisy_mask, bloqueio / "cena"))

    assert code == 1
    erro = capsys.readouterr().err
    assert erro.startswith("erro: falha ao gravar")
    assert "Traceback" not in erro
