"""Testes das operações do laboratório M1.1.

As imagens sintéticas são pequenas o bastante para conferência manual dos
valores esperados, conforme exigido pelo enunciado.
"""

import numpy as np
import pytest

from pdi_lab import operations
from pdi_lab.errors import PdiLabError

# Imagem 2x2 em BGR escolhida para cobrir preto, branco e dois tons medios.
# Linha 0: preto (0,0,0) e branco (255,255,255)
# Linha 1: (B=10, G=20, R=30) e (B=100, G=150, R=200)
SAMPLE_BGR = np.array(
    [
        [[0, 0, 0], [255, 255, 255]],
        [[10, 20, 30], [100, 150, 200]],
    ],
    dtype=np.uint8,
)


def test_round_half_up_desempata_para_cima():
    assert operations._round_half_up(0.5) == 1
    assert operations._round_half_up(1.5) == 2
    assert operations._round_half_up(2.5) == 3
    assert operations._round_half_up(2.4) == 2


def test_clamp_satura_nos_dois_extremos():
    assert operations._clamp_to_uint8(-10) == 0
    assert operations._clamp_to_uint8(300) == 255
    assert operations._clamp_to_uint8(127.5) == 128


def test_copia_e_numericamente_identica():
    result = operations.copy_image(SAMPLE_BGR)

    assert result.dtype == np.uint8
    assert result.shape == SAMPLE_BGR.shape
    assert np.array_equal(result, SAMPLE_BGR)
    assert result is not SAMPLE_BGR


def test_copia_preserva_imagem_em_niveis_de_cinza():
    gray = np.array([[0, 128], [200, 255]], dtype=np.uint8)

    result = operations.copy_image(gray)

    assert result.shape == gray.shape
    assert np.array_equal(result, gray)


def test_separacao_de_canais_preserva_apenas_o_canal_pedido():
    blue = operations.extract_channel(SAMPLE_BGR, "b")
    green = operations.extract_channel(SAMPLE_BGR, "g")
    red = operations.extract_channel(SAMPLE_BGR, "r")

    # O pixel (1,0) vale B=10, G=20, R=30 na ordem BGR do OpenCV.
    assert list(blue[1, 0]) == [10, 0, 0]
    assert list(green[1, 0]) == [0, 20, 0]
    assert list(red[1, 0]) == [0, 0, 30]

    # A soma dos tres canais isolados reconstroi a imagem original.
    assert np.array_equal(
        blue.astype(int) + green.astype(int) + red.astype(int),
        SAMPLE_BGR.astype(int),
    )


def test_media_simples_com_valores_conferidos_a_mao():
    result = operations.grayscale_average(SAMPLE_BGR)

    assert result.ndim == 2, "a saida em niveis de cinza deve ter um unico canal"
    assert result[0, 0] == 0
    assert result[1, 0] == 20  # (10 + 20 + 30) / 3
    assert result[1, 1] == 150  # (100 + 150 + 200) / 3


def test_media_simples_nao_estoura_em_pixel_branco():
    """Regressao: somar tres uint8 antes de dividir dava a volta em 253/3 = 84."""
    white = np.full((2, 2, 3), 255, dtype=np.uint8)

    result = operations.grayscale_average(white)

    assert result.min() == 255
    assert result.max() == 255


def test_media_ponderada_com_valores_conferidos_a_mao():
    result = operations.grayscale_weighted(SAMPLE_BGR)

    assert result.ndim == 2
    assert result[0, 0] == 0
    assert result[0, 1] == 255
    # 0,114*10 + 0,587*20 + 0,299*30 = 21,85 -> 22
    assert result[1, 0] == 22
    # 0,114*100 + 0,587*150 + 0,299*200 = 159,25 -> 159
    assert result[1, 1] == 159


def test_as_duas_conversoes_divergem_no_mesmo_pixel():
    average = operations.grayscale_average(SAMPLE_BGR)
    weighted = operations.grayscale_weighted(SAMPLE_BGR)

    assert average[1, 1] == 150
    assert weighted[1, 1] == 159
    assert average[1, 1] != weighted[1, 1]


def test_conversao_preserva_imagem_constante():
    constant = np.full((3, 3, 3), 90, dtype=np.uint8)

    assert operations.grayscale_average(constant).tolist() == [[90] * 3] * 3
    assert operations.grayscale_weighted(constant).tolist() == [[90] * 3] * 3


def test_imagem_de_um_unico_pixel():
    single = np.array([[[10, 20, 30]]], dtype=np.uint8)

    assert operations.copy_image(single).shape == (1, 1, 3)
    assert operations.grayscale_average(single)[0, 0] == 20
    assert operations.inspect_image(single)["pixels"] == 1


@pytest.mark.parametrize("levels", [2, 4, 8, 16])
def test_quantizacao_respeita_a_quantidade_de_niveis(levels):
    ramp = np.arange(256, dtype=np.uint8).reshape(16, 16)

    result = operations.quantize(ramp, levels)

    assert len(np.unique(result)) == levels
    assert result.min() == 0
    assert result.max() == 255


def test_quantizacao_com_valores_conferidos_a_mao():
    gray = np.array([[0, 255], [22, 159]], dtype=np.uint8)

    # levels=2: passo 255, indices 0 e 1.
    assert operations.quantize(gray, 2).tolist() == [[0, 255], [0, 255]]
    # levels=4: passo 85, indices 0, 3, 0 e 2 -> 0, 255, 0 e 170.
    assert operations.quantize(gray, 4).tolist() == [[0, 255], [0, 170]]


def test_quantizacao_preserva_os_extremos_do_intervalo():
    extremes = np.array([[0, 255]], dtype=np.uint8)

    for levels in (2, 4, 8, 16):
        result = operations.quantize(extremes, levels)
        assert result[0, 0] == 0
        assert result[0, 1] == 255


def test_quantizacao_aceita_imagem_colorida_convertendo_antes():
    result = operations.quantize(SAMPLE_BGR, 2)

    assert result.ndim == 2
    assert result.tolist() == [[0, 255], [0, 255]]


@pytest.mark.parametrize("levels", [-1, 0, 1, 257, 2.5, "8", None])
def test_quantizacao_rejeita_quantidade_invalida_de_niveis(levels):
    gray = np.array([[0, 255]], dtype=np.uint8)

    with pytest.raises(PdiLabError):
        operations.quantize(gray, levels)


def test_operacoes_de_cor_rejeitam_imagem_em_niveis_de_cinza():
    gray = np.array([[0, 128]], dtype=np.uint8)

    with pytest.raises(PdiLabError):
        operations.grayscale_average(gray)
    with pytest.raises(PdiLabError):
        operations.grayscale_weighted(gray)
    with pytest.raises(PdiLabError):
        operations.extract_channel(gray, "b")


def test_canal_invalido_e_rejeitado():
    with pytest.raises(PdiLabError):
        operations.extract_channel(SAMPLE_BGR, "x")


def test_inspecao_calcula_estatisticas_globais_e_por_canal():
    stats = operations.inspect_image(SAMPLE_BGR)

    assert stats["width"] == 2
    assert stats["height"] == 2
    assert stats["channels"] == 3
    assert stats["pixels"] == 4  # largura x altura, sem multiplicar canais
    assert stats["type"] == "uint8"
    assert stats["min"] == 0
    assert stats["max"] == 255

    # Canal azul: 0, 255, 10 e 100 -> media 91,25.
    assert stats["min_b"] == 0
    assert stats["max_b"] == 255
    assert stats["mean_b"] == pytest.approx(91.25)
    # Canal verde: 0, 255, 20 e 150 -> media 106,25.
    assert stats["mean_g"] == pytest.approx(106.25)
    # Canal vermelho: 0, 255, 30 e 200 -> media 121,25.
    assert stats["mean_r"] == pytest.approx(121.25)


def test_inspecao_de_imagem_em_niveis_de_cinza_nao_reporta_canais():
    gray = np.array([[0, 100], [200, 255]], dtype=np.uint8)

    stats = operations.inspect_image(gray)

    assert stats["channels"] == 1
    assert stats["pixels"] == 4
    assert stats["min"] == 0
    assert stats["max"] == 255
    assert stats["mean"] == pytest.approx(138.75)
    assert "mean_b" not in stats


def test_formatacao_da_inspecao_usa_pares_chave_valor():
    text = operations.format_inspection(operations.inspect_image(SAMPLE_BGR))
    lines = text.splitlines()

    assert lines[0] == "width=2"
    assert lines[1] == "height=2"
    assert lines[2] == "channels=3"
    assert lines[3] == "pixels=4"
    assert lines[4] == "type=uint8"
