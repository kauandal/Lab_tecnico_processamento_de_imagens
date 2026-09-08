"""Testes da interface de linha de comando e dos códigos de saída."""

import cv2 as cv
import numpy as np
import pytest

from pdi_lab.cli import main

SAMPLE_BGR = np.array(
    [
        [[0, 0, 0], [255, 255, 255]],
        [[10, 20, 30], [100, 150, 200]],
    ],
    dtype=np.uint8,
)


@pytest.fixture
def sample_image(tmp_path):
    """Grava a imagem de teste em disco e devolve o caminho."""
    path = tmp_path / "entrada.png"
    cv.imwrite(str(path), SAMPLE_BGR)
    return path


def test_copia_retorna_zero_e_cria_o_arquivo(tmp_path, sample_image):
    output = tmp_path / "saida" / "copy.png"

    code = main(
        [
            "--input",
            str(sample_image),
            "--output",
            str(output),
            "--operation",
            "copy",
        ]
    )

    assert code == 0
    assert output.exists()
    assert np.array_equal(cv.imread(str(output), cv.IMREAD_UNCHANGED), SAMPLE_BGR)


def test_saida_como_diretorio_gera_nome_padrao(tmp_path, sample_image):
    destination = tmp_path / "resultados"
    destination.mkdir()

    code = main(
        [
            "--input",
            str(sample_image),
            "--output",
            str(destination),
            "--operation",
            "quantize",
            "--levels",
            "4",
        ]
    )

    assert code == 0
    assert (destination / "quant_4.png").exists()


def test_inspecao_escreve_na_saida_padrao(sample_image, capsys):
    code = main(["--input", str(sample_image), "--operation", "inspect"])

    assert code == 0
    saida = capsys.readouterr().out
    assert "width=2" in saida
    assert "pixels=4" in saida
    assert "mean_b=91.2500" in saida


def test_arquivo_inexistente_retorna_um(tmp_path, capsys):
    code = main(
        [
            "--input",
            str(tmp_path / "nao_existe.png"),
            "--output",
            str(tmp_path / "saida.png"),
            "--operation",
            "copy",
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
            "copy",
        ]
    )

    assert code == 1
    assert "decodificar" in capsys.readouterr().err


def test_niveis_invalidos_retornam_um(tmp_path, sample_image, capsys):
    code = main(
        [
            "--input",
            str(sample_image),
            "--output",
            str(tmp_path / "quant.png"),
            "--operation",
            "quantize",
            "--levels",
            "1",
        ]
    )

    assert code == 1
    assert "niveis" in capsys.readouterr().err


def test_quantize_sem_levels_retorna_um(tmp_path, sample_image, capsys):
    code = main(
        [
            "--input",
            str(sample_image),
            "--output",
            str(tmp_path / "quant.png"),
            "--operation",
            "quantize",
        ]
    )

    assert code == 1
    assert "--levels" in capsys.readouterr().err


def test_operacao_de_imagem_sem_output_retorna_um(sample_image, capsys):
    code = main(["--input", str(sample_image), "--operation", "copy"])

    assert code == 1
    assert "--output" in capsys.readouterr().err


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


def test_operacao_de_cor_em_imagem_cinza_retorna_um(tmp_path, capsys):
    gray_path = tmp_path / "cinza.png"
    cv.imwrite(str(gray_path), np.array([[0, 255]], dtype=np.uint8))

    code = main(
        [
            "--input",
            str(gray_path),
            "--output",
            str(tmp_path / "saida.png"),
            "--operation",
            "grayscale_weighted",
        ]
    )

    assert code == 1
    assert "3 canais" in capsys.readouterr().err
