"""Testes da interface de linha de comando e dos códigos de saída."""

import cv2 as cv
import numpy as np
import pytest

from pdi_lab.cli import main

SAMPLE_GRAY = np.array([[0, 100], [200, 255]], dtype=np.uint8)


@pytest.fixture
def sample_image(tmp_path):
    """Grava a imagem de teste em disco e devolve o caminho."""
    path = tmp_path / "entrada.png"
    cv.imwrite(str(path), SAMPLE_GRAY)
    return path


def test_brilho_retorna_zero_e_cria_o_arquivo(tmp_path, sample_image):
    output = tmp_path / "saida" / "brightness.png"

    code = main(
        [
            "--input",
            str(sample_image),
            "--output",
            str(output),
            "--operation",
            "brightness",
            "--value",
            "50",
        ]
    )

    assert code == 0
    assert output.exists()
    resultado = cv.imread(str(output), cv.IMREAD_UNCHANGED)
    assert resultado.tolist() == [[50, 150], [250, 255]]


def test_brilho_negativo_pela_linha_de_comando(tmp_path, sample_image):
    output = tmp_path / "escuro.png"

    code = main(
        [
            "--input",
            str(sample_image),
            "--output",
            str(output),
            "--operation",
            "brightness",
            "--value",
            "-50",
        ]
    )

    assert code == 0
    assert cv.imread(str(output), cv.IMREAD_UNCHANGED).tolist() == [[0, 50], [150, 205]]


def test_histograma_gera_csv_no_formato_do_contrato(tmp_path, sample_image):
    output = tmp_path / "histogram.csv"

    code = main(
        [
            "--input",
            str(sample_image),
            "--output",
            str(output),
            "--operation",
            "histogram",
        ]
    )

    assert code == 0
    linhas = output.read_text(encoding="utf-8").strip().splitlines()
    assert linhas[0] == "intensity,count"
    assert len(linhas) == 257
    assert linhas[1] == "0,1"


def test_saida_como_diretorio_gera_nome_padrao(tmp_path, sample_image):
    destination = tmp_path / "resultados"
    destination.mkdir()

    assert (
        main(
            [
                "--input",
                str(sample_image),
                "--output",
                str(destination),
                "--operation",
                "threshold",
                "--threshold",
                "128",
            ]
        )
        == 0
    )
    assert (destination / "threshold_128.png").exists()

    assert (
        main(
            [
                "--input",
                str(sample_image),
                "--output",
                str(destination),
                "--operation",
                "contrast",
                "--alpha",
                "1.5",
            ]
        )
        == 0
    )
    assert (destination / "contrast_1_5.png").exists()


def test_arquivo_inexistente_retorna_um(tmp_path, capsys):
    code = main(
        [
            "--input",
            str(tmp_path / "nao_existe.png"),
            "--output",
            str(tmp_path / "saida.png"),
            "--operation",
            "negative",
        ]
    )

    assert code == 1
    assert "nao encontrado" in capsys.readouterr().err


def test_arquivo_corrompido_retorna_um(tmp_path, capsys):
    corrompido = tmp_path / "quebrado.png"
    corrompido.write_bytes(b"isto nao e uma imagem")

    code = main(
        [
            "--input",
            str(corrompido),
            "--output",
            str(tmp_path / "saida.png"),
            "--operation",
            "negative",
        ]
    )

    assert code == 1
    assert "decodificar" in capsys.readouterr().err


def test_limiar_fora_do_intervalo_retorna_um(tmp_path, sample_image, capsys):
    code = main(
        [
            "--input",
            str(sample_image),
            "--output",
            str(tmp_path / "saida.png"),
            "--operation",
            "threshold",
            "--threshold",
            "300",
        ]
    )

    assert code == 1
    assert "limiar invalido" in capsys.readouterr().err


def test_alpha_negativo_retorna_um(tmp_path, sample_image, capsys):
    code = main(
        [
            "--input",
            str(sample_image),
            "--output",
            str(tmp_path / "saida.png"),
            "--operation",
            "contrast",
            "--alpha",
            "-1",
        ]
    )

    assert code == 1
    assert "alpha invalido" in capsys.readouterr().err


@pytest.mark.parametrize(
    "operation,faltando",
    [
        ("brightness", "--value"),
        ("contrast", "--alpha"),
        ("threshold", "--threshold"),
    ],
)
def test_parametro_obrigatorio_ausente_retorna_um(
    tmp_path, sample_image, capsys, operation, faltando
):
    code = main(
        [
            "--input",
            str(sample_image),
            "--output",
            str(tmp_path / "saida.png"),
            "--operation",
            operation,
        ]
    )

    assert code == 1
    assert faltando in capsys.readouterr().err


def test_operacao_desconhecida_retorna_dois(tmp_path, sample_image):
    with pytest.raises(SystemExit) as excinfo:
        main(
            [
                "--input",
                str(sample_image),
                "--output",
                str(tmp_path / "saida.png"),
                "--operation",
                "inexistente",
            ]
        )

    assert excinfo.value.code == 2


def test_valor_nao_numerico_retorna_dois(tmp_path, sample_image):
    with pytest.raises(SystemExit) as excinfo:
        main(
            [
                "--input",
                str(sample_image),
                "--output",
                str(tmp_path / "saida.png"),
                "--operation",
                "brightness",
                "--value",
                "muito",
            ]
        )

    assert excinfo.value.code == 2
