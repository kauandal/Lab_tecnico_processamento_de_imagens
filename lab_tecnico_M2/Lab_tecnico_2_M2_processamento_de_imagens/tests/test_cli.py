"""Testes da interface de linha de comando e dos códigos de saída."""

import cv2 as cv
import numpy as np
import pytest

from pdi_lab.cli import main


@pytest.fixture
def gray_image(tmp_path):
    """Quadrado claro sobre fundo escuro, com um pixel exatamente no limiar."""
    image = np.full((9, 9), 30, dtype=np.uint8)
    image[3:6, 3:6] = 200
    image[0, 0] = 120
    path = tmp_path / "entrada.png"
    cv.imwrite(str(path), image)
    return path


@pytest.fixture
def color_image(tmp_path):
    """Faixa vermelha (matiz perto de 0) sobre fundo verde."""
    hsv = np.zeros((6, 6, 3), dtype=np.uint8)
    hsv[:] = (60, 255, 255)
    hsv[:, :2] = (178, 255, 255)
    hsv[:, 2:3] = (3, 255, 255)
    path = tmp_path / "colorida.png"
    cv.imwrite(str(path), cv.cvtColor(hsv, cv.COLOR_HSV2BGR))
    return path


def segment_args(input_path, output_path, *extra):
    return [
        "--input",
        str(input_path),
        "--output",
        str(output_path),
        "--operation",
        "segment",
        *extra,
    ]


def read_mask(path):
    return cv.imread(str(path), cv.IMREAD_UNCHANGED)


def test_fixed_gera_mascara_valida(tmp_path, gray_image, capsys):
    output = tmp_path / "saida" / "mask.png"

    code = main(segment_args(gray_image, output, "--method", "fixed", "--threshold", "120"))

    assert code == 0
    mask = read_mask(output)
    assert mask.shape == (9, 9)
    assert mask.ndim == 2
    assert set(np.unique(mask).tolist()) <= {0, 255}
    assert mask[0, 0] == 0, "pixel igual ao limiar deve ir para o fundo"
    assert np.count_nonzero(mask) == 9
    stdout = capsys.readouterr().out
    assert "binary_check=ok" in stdout
    assert "foreground=9" in stdout


def test_otsu_informa_limiar_calculado(tmp_path, gray_image, capsys):
    code = main(segment_args(gray_image, tmp_path / "otsu.png", "--method", "otsu"))

    assert code == 0
    assert "otsu_threshold=" in capsys.readouterr().out


def test_adaptive_pela_linha_de_comando(tmp_path, gray_image):
    output = tmp_path / "adaptive.png"

    code = main(
        segment_args(
            gray_image,
            output,
            "--method",
            "adaptive",
            "--block-size",
            "9",
            "--c",
            "-5",
            "--adaptive-kind",
            "mean",
        )
    )

    assert code == 0
    assert read_mask(output)[4, 4] == 255


def test_hsv_com_faixa_que_cruza_o_zero(tmp_path, color_image, capsys):
    output = tmp_path / "hsv.png"

    code = main(
        segment_args(
            color_image,
            output,
            "--method",
            "hsv",
            "--hsv-lower",
            "170,100,100",
            "--hsv-upper",
            "10,255,255",
        )
    )

    assert code == 0
    mask = read_mask(output)
    assert np.all(mask[:, :3] == 255)
    assert np.all(mask[:, 3:] == 0)
    assert "hue_wraparound=True" in capsys.readouterr().out


def test_invert_troca_objeto_e_fundo(tmp_path, gray_image):
    normal = tmp_path / "normal.png"
    invertida = tmp_path / "invertida.png"
    base = ("--method", "fixed", "--threshold", "120")

    assert main(segment_args(gray_image, normal, *base)) == 0
    assert main(segment_args(gray_image, invertida, *base, "--invert")) == 0
    assert np.array_equal(read_mask(invertida), 255 - read_mask(normal))


def test_sobreposicao(tmp_path, gray_image):
    overlay = tmp_path / "overlay.png"

    code = main(
        segment_args(
            gray_image,
            tmp_path / "mask.png",
            "--method",
            "fixed",
            "--threshold",
            "120",
            "--blur",
            "3",
            "--overlay",
            str(overlay),
        )
    )

    assert code == 0
    assert read_mask(overlay).shape == (9, 9, 3)


@pytest.mark.parametrize("name", ["saida", "pasta.png"], ids=["sem_extensao", "diretorio"])
def test_saida_precisa_ser_o_arquivo_exato(tmp_path, gray_image, name):
    """A máscara vai só para o caminho exato de --output, nunca para dentro de uma pasta."""
    destino = tmp_path / name
    if name.endswith(".png"):
        destino.mkdir()

    code = main(segment_args(gray_image, destino, "--method", "otsu"))

    assert code == 1
    assert not any(destino.glob("*")) if destino.is_dir() else not destino.exists()


def test_falha_de_gravacao(tmp_path, gray_image, capsys):
    """A pasta pai é um arquivo, então a gravação falha com mensagem clara."""
    bloqueio = tmp_path / "arquivo.txt"
    bloqueio.write_text("x", encoding="utf-8")

    code = main(segment_args(gray_image, bloqueio / "mask.png", "--method", "otsu"))

    assert code == 1
    erro = capsys.readouterr().err
    assert erro.startswith("erro: falha ao gravar")
    assert "Traceback" not in erro


# --- falhas --------------------------------------------------------------


def test_arquivo_inexistente(tmp_path, capsys):
    code = main(
        segment_args(
            tmp_path / "nao_existe.png",
            tmp_path / "mask.png",
            "--method",
            "fixed",
            "--threshold",
            "120",
        )
    )

    assert code == 1
    assert "erro:" in capsys.readouterr().err


def test_arquivo_que_nao_e_imagem(tmp_path):
    falso = tmp_path / "falso.png"
    falso.write_text("isto nao e uma imagem", encoding="utf-8")

    code = main(segment_args(falso, tmp_path / "mask.png", "--method", "otsu"))

    assert code == 1


def test_metodo_desconhecido(tmp_path, gray_image):
    with pytest.raises(SystemExit) as excinfo:
        main(segment_args(gray_image, tmp_path / "mask.png", "--method", "kmeans"))

    assert excinfo.value.code != 0


def test_operacao_desconhecida(tmp_path, gray_image):
    with pytest.raises(SystemExit) as excinfo:
        main(
            [
                "--input",
                str(gray_image),
                "--output",
                str(tmp_path / "mask.png"),
                "--operation",
                "watershed",
                "--method",
                "otsu",
            ]
        )

    assert excinfo.value.code != 0


@pytest.mark.parametrize(
    "extra",
    [
        (),
        ("--method", "fixed"),
        ("--method", "fixed", "--threshold", "300"),
        ("--method", "fixed", "--threshold", "-1"),
        ("--method", "otsu", "--blur", "4"),
        ("--method", "adaptive", "--block-size", "8", "--c", "0"),
        ("--method", "adaptive"),
        ("--method", "hsv", "--hsv-lower", "0,0,0"),
        ("--method", "hsv", "--hsv-lower", "0,0,0", "--hsv-upper", "200,255,255"),
    ],
    ids=[
        "segment_sem_metodo",
        "fixed_sem_limiar",
        "limiar_acima_de_255",
        "limiar_negativo",
        "blur_par",
        "bloco_par",
        "adaptive_sem_c",
        "hsv_sem_limite_superior",
        "hsv_matiz_acima_de_179",
    ],
)
def test_parametros_invalidos(tmp_path, gray_image, extra):
    output = tmp_path / "mask.png"

    code = main(segment_args(gray_image, output, *extra))

    assert code == 1
    assert not output.exists()


def test_hsv_em_imagem_cinza(tmp_path, gray_image):
    code = main(
        segment_args(
            gray_image,
            tmp_path / "mask.png",
            "--method",
            "hsv",
            "--hsv-lower",
            "0,0,0",
            "--hsv-upper",
            "10,255,255",
        )
    )

    assert code == 1


@pytest.mark.parametrize("name", ["mask.jpg", "mask.jpeg", "mask.webp"])
def test_saida_com_perdas_e_recusada(tmp_path, gray_image, name):
    output = tmp_path / name

    code = main(segment_args(gray_image, output, "--method", "otsu"))

    assert code == 1
    assert not output.exists()
