"""Testes das operações do laboratório M1.2.

A imagem sintética é pequena o bastante para conferência manual dos valores
esperados, conforme exigido pelo enunciado.
"""

import numpy as np
import pytest

from pdi_lab import operations
from pdi_lab.errors import PdiLabError

# Imagem 2x2 em niveis de cinza cobrindo os dois extremos e dois tons medios.
SAMPLE_GRAY = np.array([[0, 100], [200, 255]], dtype=np.uint8)

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
    assert operations._round_half_up(191.5) == 192


def test_clamp_satura_nos_dois_extremos():
    assert operations._clamp_to_uint8(-64) == 0
    assert operations._clamp_to_uint8(318.5) == 255
    assert operations._clamp_to_uint8(127.5) == 128


def test_conversao_para_cinza_com_valores_conferidos_a_mao():
    result = operations.to_grayscale(SAMPLE_BGR)

    assert result.ndim == 2
    assert result[0, 0] == 0
    assert result[0, 1] == 255
    # 0,114*10 + 0,587*20 + 0,299*30 = 21,85 -> 22
    assert result[1, 0] == 22
    # 0,114*100 + 0,587*150 + 0,299*200 = 159,25 -> 159
    assert result[1, 1] == 159


def test_conversao_nao_altera_imagem_ja_em_cinza():
    result = operations.to_grayscale(SAMPLE_GRAY)

    assert np.array_equal(result, SAMPLE_GRAY)


def test_brilho_positivo_com_valores_conferidos_a_mao():
    result = operations.brightness(SAMPLE_GRAY, 50)

    # 255 + 50 satura em 255.
    assert result.tolist() == [[50, 150], [250, 255]]


def test_brilho_negativo_com_valores_conferidos_a_mao():
    result = operations.brightness(SAMPLE_GRAY, -50)

    # 0 - 50 satura em 0.
    assert result.tolist() == [[0, 50], [150, 205]]


def test_brilho_zero_e_identidade():
    result = operations.brightness(SAMPLE_GRAY, 0)

    assert np.array_equal(result, SAMPLE_GRAY)


def test_brilho_extremo_achata_a_imagem_contra_o_limite():
    assert operations.brightness(SAMPLE_GRAY, 300).tolist() == [[255, 255], [255, 255]]
    assert operations.brightness(SAMPLE_GRAY, -300).tolist() == [[0, 0], [0, 0]]


def test_brilho_nao_da_a_volta_no_uint8():
    """Regressao: somar direto em uint8 faria 200 + 100 virar 44."""
    result = operations.brightness(np.array([[200]], dtype=np.uint8), 100)

    assert result[0, 0] == 255


def test_contraste_identidade_preserva_a_imagem():
    result = operations.contrast(SAMPLE_GRAY, 1.0)

    assert np.array_equal(result, SAMPLE_GRAY)


def test_contraste_reduzido_aproxima_do_centro():
    result = operations.contrast(SAMPLE_GRAY, 0.5)

    # 0,5*(0-128)+128 = 64;  0,5*(100-128)+128 = 114
    # 0,5*(200-128)+128 = 164;  0,5*(255-128)+128 = 191,5 -> 192
    assert result.tolist() == [[64, 114], [164, 192]]


def test_contraste_ampliado_afasta_do_centro_e_satura():
    result = operations.contrast(SAMPLE_GRAY, 1.5)

    # 1,5*(0-128)+128 = -64 -> 0;   1,5*(100-128)+128 = 86
    # 1,5*(200-128)+128 = 236;      1,5*(255-128)+128 = 318,5 -> 255
    assert result.tolist() == [[0, 86], [236, 255]]


def test_contraste_zero_achata_tudo_no_ponto_fixo():
    result = operations.contrast(SAMPLE_GRAY, 0.0)

    assert result.tolist() == [[128, 128], [128, 128]]


def test_contraste_preserva_o_ponto_fixo():
    pivot = np.array([[128]], dtype=np.uint8)

    for alpha in (0.5, 1.0, 1.5, 3.0):
        assert operations.contrast(pivot, alpha)[0, 0] == 128


def test_negativo_com_valores_conferidos_a_mao():
    result = operations.negative(SAMPLE_GRAY)

    assert result.tolist() == [[255, 155], [55, 0]]


def test_negativo_aplicado_duas_vezes_devolve_a_original():
    result = operations.negative(operations.negative(SAMPLE_GRAY))

    assert np.array_equal(result, SAMPLE_GRAY)


def test_limiarizacao_com_dois_limiares_distintos():
    assert operations.threshold(SAMPLE_GRAY, 128).tolist() == [[0, 0], [255, 255]]
    assert operations.threshold(SAMPLE_GRAY, 64).tolist() == [[0, 255], [255, 255]]


def test_limiarizacao_inclui_o_proprio_limiar():
    """O criterio e maior ou igual, entao o pixel igual ao limiar vira 255."""
    assert operations.threshold(np.array([[200]], dtype=np.uint8), 200)[0, 0] == 255
    assert operations.threshold(np.array([[199]], dtype=np.uint8), 200)[0, 0] == 0


def test_limiarizacao_nos_extremos_do_intervalo():
    assert operations.threshold(SAMPLE_GRAY, 0).tolist() == [[255, 255], [255, 255]]
    assert operations.threshold(SAMPLE_GRAY, 255).tolist() == [[0, 0], [0, 255]]


def test_limiarizacao_produz_apenas_dois_valores():
    result = operations.threshold(SAMPLE_GRAY, 128)

    assert sorted(np.unique(result).tolist()) == [0, 255]


def test_histograma_conta_todos_os_pixels():
    counts = operations.histogram(SAMPLE_GRAY)

    assert len(counts) == 256
    assert sum(counts) == SAMPLE_GRAY.size
    assert counts[0] == 1
    assert counts[100] == 1
    assert counts[200] == 1
    assert counts[255] == 1
    assert counts[50] == 0


def test_histograma_de_imagem_constante_concentra_em_um_nivel():
    constant = np.full((4, 4), 90, dtype=np.uint8)

    counts = operations.histogram(constant)

    assert counts[90] == 16
    assert sum(counts) == 16


def test_histograma_da_limiarizacao_tem_apenas_dois_niveis_ocupados():
    binary = operations.threshold(SAMPLE_GRAY, 128)

    counts = operations.histogram(binary)

    assert counts[0] == 2
    assert counts[255] == 2
    assert sum(counts) == 4


def test_brilho_desloca_o_histograma():
    original = operations.histogram_summary(operations.histogram(SAMPLE_GRAY))
    deslocado = operations.histogram_summary(
        operations.histogram(operations.brightness(SAMPLE_GRAY, 50))
    )

    assert deslocado["mean"] > original["mean"]


def test_formato_csv_do_histograma():
    text = operations.format_histogram(operations.histogram(SAMPLE_GRAY))
    lines = text.splitlines()

    assert lines[0] == "intensity,count"
    assert len(lines) == 257  # cabecalho mais 256 linhas de dados
    assert lines[1] == "0,1"
    assert lines[256] == "255,1"


def test_formato_csv_rejeita_histograma_de_tamanho_errado():
    with pytest.raises(PdiLabError):
        operations.format_histogram([0] * 10)


def test_resumo_do_histograma():
    resumo = operations.histogram_summary(operations.histogram(SAMPLE_GRAY))

    assert resumo["pixels"] == 4
    assert resumo["mean"] == pytest.approx((0 + 100 + 200 + 255) / 4)
    assert resumo["min"] == 0
    assert resumo["max"] == 255
    assert resumo["levels_used"] == 4
    assert resumo["at_zero"] == 1
    assert resumo["at_max"] == 1


def test_operacoes_aceitam_imagem_colorida_convertendo_antes():
    result = operations.negative(SAMPLE_BGR)

    assert result.ndim == 2
    # O cinza ponderado de (10,20,30) e 22, logo o negativo e 233.
    assert result[1, 0] == 233


def test_imagem_de_um_unico_pixel():
    single = np.array([[42]], dtype=np.uint8)

    assert operations.brightness(single, 10)[0, 0] == 52
    assert operations.negative(single)[0, 0] == 213
    assert sum(operations.histogram(single)) == 1


@pytest.mark.parametrize("alpha", [-0.5, float("nan"), float("inf"), "1.5", None])
def test_contraste_rejeita_alpha_invalido(alpha):
    with pytest.raises(PdiLabError):
        operations.contrast(SAMPLE_GRAY, alpha)


@pytest.mark.parametrize("value", [-1, 256, 300, 1.5, "128", None])
def test_limiarizacao_rejeita_limiar_invalido(value):
    with pytest.raises(PdiLabError):
        operations.threshold(SAMPLE_GRAY, value)


@pytest.mark.parametrize("value", [1.5, "50", None])
def test_brilho_rejeita_valor_invalido(value):
    with pytest.raises(PdiLabError):
        operations.brightness(SAMPLE_GRAY, value)
