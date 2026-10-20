"""Testes da interface de linha de comando e dos códigos de saída."""

from pathlib import Path

import cv2 as cv
import numpy as np
import pytest

from pdi_lab.cli import main

PROJECT_KERNELS = Path(__file__).resolve().parent.parent / "kernels"
IDENTITY = str(PROJECT_KERNELS / "identity_3x3.txt")


@pytest.fixture
def sample_image(tmp_path):
    """Quadrado claro sobre fundo escuro, gravado em disco."""
    image = np.zeros((9, 9), dtype=np.uint8)
    image[3:6, 3:6] = 200
    path = tmp_path / "entrada.png"
    cv.imwrite(str(path), image)
    return path


def test_convolucao_identidade_reproduz_a_entrada(tmp_path, sample_image):
    output = tmp_path / "saida" / "id.png"

    code = main(
        [
            "--input",
            str(sample_image),
            "--output",
            str(output),
            "--operation",
            "convolution",
            "--kernel",
            IDENTITY,
            "--border",
            "replicate",
        ]
    )

    assert code == 0
    assert output.exists()
    entrada = cv.imread(str(sample_image), cv.IMREAD_UNCHANGED)
    assert np.array_equal(cv.imread(str(output), cv.IMREAD_UNCHANGED), entrada)


def test_media_pela_linha_de_comando(tmp_path, sample_image):
    output = tmp_path / "mean.png"

    code = main(
        [
            "--input",
            str(sample_image),
            "--output",
            str(output),
            "--operation",
            "mean_filter",
            "--size",
            "5",
        ]
    )

    assert code == 0
    assert output.exists()


def test_sobel_grava_a_componente_pedida(tmp_path, sample_image):
    destino = tmp_path / "saidas"
    destino.mkdir()

    for componente in ("gx", "gy", "l1", "l2"):
        code = main(
            [
                "--input",
                str(sample_image),
                "--output",
                str(destino),
                "--operation",
                "sobel",
                "--component",
                componente,
                "--border",
                "replicate",
            ]
        )
        assert code == 0
        assert (destino / ("sobel_" + componente + "_replicate.png")).exists()


def test_nome_padrao_registra_a_estrategia_de_borda(tmp_path, sample_image):
    destino = tmp_path / "saidas"
    destino.mkdir()

    for borda in ("copy", "replicate"):
        code = main(
            [
                "--input",
                str(sample_image),
                "--output",
                str(destino),
                "--operation",
                "mean_filter",
                "--size",
                "3",
                "--border",
                borda,
            ]
        )
        assert code == 0
        assert (destino / ("mean_3x3_" + borda + ".png")).exists()


def test_laplaciano_grava_resposta_bruta_em_csv(tmp_path, sample_image):
    output = tmp_path / "lap.png"
    raw = tmp_path / "lap_raw.csv"

    code = main(
        [
            "--input",
            str(sample_image),
            "--output",
            str(output),
            "--operation",
            "laplacian",
            "--raw-output",
            str(raw),
        ]
    )

    assert code == 0
    assert output.exists()

    linhas = raw.read_text(encoding="utf-8").strip().splitlines()
    assert len(linhas) == 9
    valores = [float(v) for v in linhas[3].split(",")]
    assert len(valores) == 9
    # A resposta bruta preserva o sinal negativo, que a imagem de 8 bits perde.
    assert min(min(float(v) for v in linha.split(",")) for linha in linhas) < 0


def test_realce_laplaciano_pela_linha_de_comando(tmp_path, sample_image):
    output = tmp_path / "realce.png"

    code = main(
        [
            "--input",
            str(sample_image),
            "--output",
            str(output),
            "--operation",
            "laplacian_enhance",
            "--alpha",
            "1.0",
        ]
    )

    assert code == 0
    assert output.exists()


def test_view_escolhida_altera_o_resultado(tmp_path, sample_image):
    com_offset = tmp_path / "offset.png"
    com_abs = tmp_path / "abs.png"

    for destino, view in ((com_offset, "offset"), (com_abs, "abs")):
        assert (
            main(
                [
                    "--input",
                    str(sample_image),
                    "--output",
                    str(destino),
                    "--operation",
                    "laplacian",
                    "--view",
                    view,
                ]
            )
            == 0
        )

    a = cv.imread(str(com_offset), cv.IMREAD_UNCHANGED)
    b = cv.imread(str(com_abs), cv.IMREAD_UNCHANGED)
    assert not np.array_equal(a, b)


def test_convolucao_sem_kernel_retorna_um(tmp_path, sample_image, capsys):
    code = main(
        [
            "--input",
            str(sample_image),
            "--output",
            str(tmp_path / "saida.png"),
            "--operation",
            "convolution",
        ]
    )

    assert code == 1
    assert "--kernel" in capsys.readouterr().err


def test_kernel_inexistente_retorna_um(tmp_path, sample_image, capsys):
    code = main(
        [
            "--input",
            str(sample_image),
            "--output",
            str(tmp_path / "saida.png"),
            "--operation",
            "convolution",
            "--kernel",
            str(tmp_path / "nao_existe.txt"),
        ]
    )

    assert code == 1
    assert "kernel nao encontrado" in capsys.readouterr().err


def test_kernel_par_retorna_um(tmp_path, sample_image, capsys):
    kernel = tmp_path / "par.txt"
    kernel.write_text("2 2\n1 1\n1 1\n", encoding="utf-8")

    code = main(
        [
            "--input",
            str(sample_image),
            "--output",
            str(tmp_path / "saida.png"),
            "--operation",
            "convolution",
            "--kernel",
            str(kernel),
        ]
    )

    assert code == 1
    assert "impar" in capsys.readouterr().err


def test_tamanho_par_de_media_retorna_um(tmp_path, sample_image, capsys):
    code = main(
        [
            "--input",
            str(sample_image),
            "--output",
            str(tmp_path / "saida.png"),
            "--operation",
            "mean_filter",
            "--size",
            "4",
        ]
    )

    assert code == 1
    assert "impar" in capsys.readouterr().err


def test_arquivo_de_entrada_inexistente_retorna_um(tmp_path, capsys):
    code = main(
        [
            "--input",
            str(tmp_path / "nao_existe.png"),
            "--output",
            str(tmp_path / "saida.png"),
            "--operation",
            "laplacian",
        ]
    )

    assert code == 1
    assert "nao encontrado" in capsys.readouterr().err


def test_borda_invalida_retorna_dois(tmp_path, sample_image):
    with pytest.raises(SystemExit) as excinfo:
        main(
            [
                "--input",
                str(sample_image),
                "--output",
                str(tmp_path / "saida.png"),
                "--operation",
                "mean_filter",
                "--border",
                "espelhar",
            ]
        )

    assert excinfo.value.code == 2


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


def test_view_invalida_retorna_dois(tmp_path, sample_image):
    with pytest.raises(SystemExit) as excinfo:
        main(
            [
                "--input",
                str(sample_image),
                "--output",
                str(tmp_path / "saida.png"),
                "--operation",
                "laplacian",
                "--view",
                "colorido",
            ]
        )

    assert excinfo.value.code == 2
