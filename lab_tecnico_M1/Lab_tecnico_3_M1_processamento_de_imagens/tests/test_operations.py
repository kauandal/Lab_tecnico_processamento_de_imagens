"""Testes das operações de vizinhança do laboratório M1.3.

As imagens sintéticas são pequenas o bastante para que o resultado possa ser
previsto antes da execução, conforme exigido pelo enunciado.
"""

import numpy as np
import pytest

from pdi_lab import kernels, operations
from pdi_lab.errors import PdiLabError

BORDERS = (operations.BORDER_COPY, operations.BORDER_REPLICATE)


def constant_image(value=100, size=5):
    """Imagem constante, usada para verificar a soma dos coeficientes."""
    return np.full((size, size), value, dtype=np.uint8)


def impulse_image(size=5, value=255):
    """Imagem preta com um único pixel claro no centro."""
    image = np.zeros((size, size), dtype=np.uint8)
    image[size // 2, size // 2] = value
    return image


def vertical_step(width=6, height=5, boundary=3):
    """Degrau vertical: colunas à esquerda escuras, à direita claras."""
    image = np.zeros((height, width), dtype=np.uint8)
    for y in range(height):
        for x in range(boundary, width):
            image[y, x] = 255
    return image


def horizontal_step(width=5, height=6, boundary=3):
    """Degrau horizontal: linhas de cima escuras, de baixo claras."""
    image = np.zeros((height, width), dtype=np.uint8)
    for y in range(boundary, height):
        for x in range(width):
            image[y, x] = 255
    return image


def square_image(size=9, side=3, value=200):
    """Forma geométrica simples: quadrado claro centrado em fundo escuro."""
    image = np.zeros((size, size), dtype=np.uint8)
    start = (size - side) // 2
    for y in range(start, start + side):
        for x in range(start, start + side):
            image[y, x] = value
    return image


# Convolução genérica


@pytest.mark.parametrize("border", BORDERS)
def test_identidade_reproduz_a_imagem(border):
    image = square_image()

    result = operations.convolve(image, kernels.IDENTITY_3X3, border)

    assert np.array_equal(operations.to_uint8(result), image)


@pytest.mark.parametrize("border", BORDERS)
def test_media_preserva_imagem_constante(border):
    image = constant_image(100)

    result = operations.mean_filter(image, 3, border)

    assert operations.to_uint8(result).tolist() == image.tolist()


def test_media_5x5_tambem_preserva_constante():
    image = constant_image(100, size=9)

    result = operations.mean_filter(image, 5, operations.BORDER_REPLICATE)

    assert operations.to_uint8(result).tolist() == image.tolist()


def test_resposta_ao_impulso_espalha_o_valor_em_nove_posicoes():
    """255 dividido por 9 da 28,33; cada posicao alcancada recebe esse valor."""
    image = impulse_image()

    result = operations.mean_filter(image, 3, operations.BORDER_REPLICATE)

    centro = result[2, 2]
    assert centro == pytest.approx(255 / 9)
    assert result[1, 1] == pytest.approx(255 / 9)
    assert result[3, 3] == pytest.approx(255 / 9)
    # Fora da vizinhanca de 3 por 3 em torno do impulso, a resposta e zero.
    assert result[0, 0] == pytest.approx(0.0)
    assert operations.to_uint8(result)[2, 2] == 28


def test_impulso_reproduz_a_forma_do_kernel():
    """Com correlacao, a resposta ao impulso reproduz o kernel sem espelhar."""
    image = np.zeros((5, 5), dtype=np.uint8)
    image[2, 2] = 1
    kernel = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]

    result = operations.convolve(image, kernel, operations.BORDER_REPLICATE)

    # A ancora em (2,2) ve o impulso na posicao relativa (0,0) do kernel, logo
    # recebe o coeficiente central. O vizinho acima e a esquerda ve o impulso
    # na posicao (+1,+1), recebendo o coeficiente 9.
    assert result[2, 2] == 5.0
    assert result[1, 1] == 9.0
    assert result[3, 3] == 1.0


def test_media_reduz_a_variacao_local():
    image = impulse_image(size=7)

    suavizada = operations.mean_filter(image, 3, operations.BORDER_REPLICATE)
    mais_suavizada = operations.mean_filter(image, 5, operations.BORDER_REPLICATE)

    assert suavizada.max() < float(image.max())
    assert mais_suavizada.max() < suavizada.max()


def test_media_ponderada_pesa_mais_o_centro_que_a_media_simples():
    image = impulse_image(size=7)

    simples = operations.mean_filter(image, 3, operations.BORDER_REPLICATE)
    ponderada = operations.weighted_mean(image, operations.BORDER_REPLICATE)

    # 255 * 4/16 = 63,75 contra 255/9 = 28,33.
    assert ponderada[3, 3] == pytest.approx(255 * 4 / 16)
    assert ponderada[3, 3] > simples[3, 3]


def test_media_ponderada_preserva_constante():
    image = constant_image(90)

    result = operations.weighted_mean(image, operations.BORDER_REPLICATE)

    assert operations.to_uint8(result).tolist() == image.tolist()


# Tratamento de bordas


def test_copy_preserva_a_moldura_da_entrada():
    image = square_image(size=7, side=3)

    result = operations.to_uint8(
        operations.mean_filter(image, 3, operations.BORDER_COPY)
    )

    assert result[0].tolist() == image[0].tolist()
    assert result[-1].tolist() == image[-1].tolist()
    assert result[:, 0].tolist() == image[:, 0].tolist()
    assert result[:, -1].tolist() == image[:, -1].tolist()


def test_copy_e_replicate_diferem_apenas_na_faixa_de_borda():
    """A largura da faixa afetada corresponde ao raio do kernel.

    A imagem tem uma barra clara encostada na borda esquerda, para que a
    moldura contenha variacao e as duas estrategias possam divergir.
    """
    image = np.zeros((9, 9), dtype=np.uint8)
    for y in range(9):
        image[y, 0] = 255
        image[y, 1] = 255

    com_copy = operations.mean_filter(image, 3, operations.BORDER_COPY)
    com_replicate = operations.mean_filter(image, 3, operations.BORDER_REPLICATE)

    # O interior, longe da moldura, e identico nas duas estrategias.
    assert np.allclose(com_copy[1:-1, 1:-1], com_replicate[1:-1, 1:-1])
    # A moldura difere, porque copy nao filtra e replicate filtra.
    assert not np.allclose(com_copy[0], com_replicate[0])


def test_raio_maior_alarga_a_faixa_de_borda_preservada():
    image = square_image(size=11, side=5)

    com_copy = operations.mean_filter(image, 5, operations.BORDER_COPY)

    # Kernel 5 por 5 tem raio 2, logo duas linhas e colunas ficam intactas.
    assert com_copy[0].tolist() == [float(v) for v in image[0]]
    assert com_copy[1].tolist() == [float(v) for v in image[1]]
    assert not np.allclose(com_copy[2], [float(v) for v in image[2]])


def test_replicate_processa_toda_a_imagem():
    """Numa imagem constante com objeto na borda, replicate suaviza ate a moldura."""
    image = np.zeros((5, 5), dtype=np.uint8)
    for y in range(5):
        image[y, 0] = 255  # barra clara encostada na borda esquerda

    result = operations.mean_filter(image, 3, operations.BORDER_REPLICATE)

    # Na coluna 0, a replicacao repete a propria barra, entao dois tercos da
    # vizinhanca valem 255: 2/3 de 255 da 170.
    assert result[2, 0] == pytest.approx(255 * 6 / 9)
    # Na coluna 1, apenas um terco da vizinhanca vale 255.
    assert result[2, 1] == pytest.approx(255 * 3 / 9)


def test_replicate_no_canto_reutiliza_o_pixel_do_canto():
    image = np.arange(9, dtype=np.uint8).reshape(3, 3)

    result = operations.convolve(
        image, kernels.IDENTITY_3X3, operations.BORDER_REPLICATE
    )

    assert result[0, 0] == 0.0
    assert result[2, 2] == 8.0


def test_estrategia_de_borda_invalida():
    with pytest.raises(PdiLabError, match="borda invalida"):
        operations.convolve(constant_image(), kernels.IDENTITY_3X3, "espelhar")


def test_convolucao_recusa_kernel_par():
    with pytest.raises(PdiLabError, match="impar"):
        operations.convolve(constant_image(), [[1.0, 1.0], [1.0, 1.0]])


def test_convolucao_recusa_kernel_vazio():
    with pytest.raises(PdiLabError, match="vazio"):
        operations.convolve(constant_image(), [])


# Laplaciano


def test_laplaciano_anula_regiao_constante():
    image = constant_image(100, size=7)

    result = operations.laplacian(image, operations.BORDER_REPLICATE)

    assert np.allclose(result, 0.0)


def test_laplaciano_com_centro_mais_claro_responde_negativo():
    """Exemplo do material: vizinhos 100 e centro 150 dao -200."""
    image = np.full((3, 3), 100, dtype=np.uint8)
    image[1, 1] = 150

    result = operations.laplacian(image, operations.BORDER_REPLICATE)

    assert result[1, 1] == -200.0


def test_laplaciano_com_centro_mais_escuro_responde_positivo():
    """Exemplo do material: vizinhos 100 e centro 50 dao +200."""
    image = np.full((3, 3), 100, dtype=np.uint8)
    image[1, 1] = 50

    result = operations.laplacian(image, operations.BORDER_REPLICATE)

    assert result[1, 1] == 200.0


def test_laplaciano_produz_sinais_opostos_nos_lados_da_transicao():
    image = vertical_step(width=8, height=3, boundary=4)

    result = operations.laplacian(image, operations.BORDER_REPLICATE)

    esquerda = result[1, 3]
    direita = result[1, 4]
    assert esquerda > 0
    assert direita < 0
    assert esquerda == pytest.approx(-direita)


def test_laplaciano_bruto_contem_valores_fora_de_8_bits():
    image = impulse_image(size=5)

    result = operations.laplacian(image, operations.BORDER_REPLICATE)

    assert result.min() < 0
    assert result.dtype == np.float64


def test_realce_equivale_ao_kernel_de_afiamento():
    """Com fator 1, g = f - L corresponde ao kernel [0 -1 0; -1 5 -1; 0 -1 0]."""
    image = square_image(size=7, side=3, value=200)

    realce = operations.laplacian_enhance(image, operations.BORDER_REPLICATE, 1.0)
    equivalente = operations.convolve(
        image,
        [[0.0, -1.0, 0.0], [-1.0, 5.0, -1.0], [0.0, -1.0, 0.0]],
        operations.BORDER_REPLICATE,
    )

    assert realce.tolist() == operations.to_uint8(equivalente).tolist()


def test_realce_com_fator_zero_devolve_a_imagem():
    image = square_image()

    realce = operations.laplacian_enhance(image, operations.BORDER_REPLICATE, 0.0)

    assert np.array_equal(realce, image)


def test_realce_aumenta_o_contraste_na_transicao():
    image = vertical_step(width=8, height=3, boundary=4)

    realce = operations.laplacian_enhance(image, operations.BORDER_REPLICATE, 1.0)

    # O lado escuro da transicao fica mais escuro e o claro fica mais claro.
    assert realce[1, 3] <= image[1, 3]
    assert realce[1, 4] >= image[1, 4]


@pytest.mark.parametrize("factor", [float("nan"), float("inf"), "1", None])
def test_realce_rejeita_fator_invalido(factor):
    with pytest.raises(PdiLabError):
        operations.laplacian_enhance(constant_image(), factor=factor)


# Sobel


def test_sobel_anula_regiao_constante():
    image = constant_image(120, size=7)

    responses = operations.sobel(image, operations.BORDER_REPLICATE)

    assert np.allclose(responses["gx"], 0.0)
    assert np.allclose(responses["gy"], 0.0)


def test_sobel_em_borda_vertical_com_valor_do_material():
    """Vizinhanca [[0,0,255],[0,0,255],[0,0,255]] produz Gx igual a 1020."""
    image = np.array(
        [[0, 0, 255], [0, 0, 255], [0, 0, 255]], dtype=np.uint8
    )

    responses = operations.sobel(image, operations.BORDER_REPLICATE)

    assert responses["gx"][1, 1] == 1020.0
    assert responses["gy"][1, 1] == 0.0


def test_sobel_em_borda_horizontal_com_valor_do_material():
    """Vizinhanca com a ultima linha clara produz Gy igual a 1020."""
    image = np.array(
        [[0, 0, 0], [0, 0, 0], [255, 255, 255]], dtype=np.uint8
    )

    responses = operations.sobel(image, operations.BORDER_REPLICATE)

    assert responses["gx"][1, 1] == 0.0
    assert responses["gy"][1, 1] == 1020.0


def test_gx_responde_a_borda_vertical_e_gy_fica_proximo_de_zero():
    image = vertical_step()

    responses = operations.sobel(image, operations.BORDER_REPLICATE)

    assert abs(responses["gx"]).max() == 1020.0
    assert abs(responses["gy"]).max() == 0.0


def test_gy_responde_a_borda_horizontal_e_gx_fica_proximo_de_zero():
    image = horizontal_step()

    responses = operations.sobel(image, operations.BORDER_REPLICATE)

    assert abs(responses["gy"]).max() == 1020.0
    assert abs(responses["gx"]).max() == 0.0


def test_transicao_invertida_inverte_o_sinal_e_mantem_a_magnitude():
    subindo = vertical_step()
    descendo = operations.to_uint8(
        np.array(255 - subindo.astype(np.float64))
    )

    a = operations.sobel(subindo, operations.BORDER_REPLICATE)
    b = operations.sobel(descendo, operations.BORDER_REPLICATE)

    assert np.allclose(a["gx"], -b["gx"])
    assert np.allclose(a["l2"], b["l2"])


def test_borda_diagonal_ativa_as_duas_componentes():
    image = np.zeros((7, 7), dtype=np.uint8)
    for y in range(7):
        for x in range(7):
            if x > y:
                image[y, x] = 255

    responses = operations.sobel(image, operations.BORDER_REPLICATE)

    assert abs(responses["gx"]).max() > 0
    assert abs(responses["gy"]).max() > 0


def test_magnitude_l1_e_maior_ou_igual_a_l2():
    image = square_image()

    responses = operations.sobel(image, operations.BORDER_REPLICATE)

    assert np.all(responses["l1"] >= responses["l2"] - 1e-9)


def test_magnitudes_com_valores_conferidos_a_mao():
    """Numa borda diagonal, Gx e Gy valem o mesmo em modulo."""
    image = np.array(
        [[0, 0, 0], [0, 0, 0], [0, 0, 255]], dtype=np.uint8
    )

    responses = operations.sobel(image, operations.BORDER_REPLICATE)
    gx = responses["gx"][1, 1]
    gy = responses["gy"][1, 1]

    assert responses["l1"][1, 1] == pytest.approx(abs(gx) + abs(gy))
    assert responses["l2"][1, 1] == pytest.approx((gx * gx + gy * gy) ** 0.5)


def test_sobel_bruto_ultrapassa_a_faixa_de_8_bits():
    """Um quadrado claro tem transicao subindo de um lado e descendo do outro."""
    image = square_image(size=9, side=3, value=255)

    responses = operations.sobel(image, operations.BORDER_REPLICATE)

    assert responses["gx"].max() > 255
    assert responses["gx"].min() < 0


# Visualização


def test_view_clamp_satura_nos_extremos():
    raw = np.array([[-300.0, 0.0, 127.5, 300.0]])

    result = operations.to_uint8(raw, operations.VIEW_CLAMP)

    assert result.tolist() == [[0, 0, 128, 255]]


def test_view_abs_descarta_o_sinal():
    raw = np.array([[-200.0, 200.0]])

    result = operations.to_uint8(raw, operations.VIEW_ABS)

    assert result.tolist() == [[200, 200]]


def test_view_offset_centra_o_zero_em_128():
    raw = np.array([[-128.0, 0.0, 127.0, 200.0]])

    result = operations.to_uint8(raw, operations.VIEW_OFFSET_NAME)

    assert result.tolist() == [[0, 128, 255, 255]]


def test_view_normalize_mapeia_a_faixa_observada():
    raw = np.array([[-100.0, 0.0, 100.0]])

    result = operations.to_uint8(raw, operations.VIEW_NORMALIZE)

    assert result.tolist() == [[0, 128, 255]]


def test_view_normalize_com_resposta_constante():
    raw = np.zeros((2, 2))

    result = operations.to_uint8(raw, operations.VIEW_NORMALIZE)

    assert result.tolist() == [[0, 0], [0, 0]]


def test_view_invalida():
    with pytest.raises(PdiLabError, match="visualizacao invalido"):
        operations.to_uint8(np.zeros((2, 2)), "colorido")


def test_resumo_da_resposta_bruta():
    raw = np.array([[-200.0, 0.0], [300.0, 10.0]])

    resumo = operations.response_summary(raw)

    assert resumo["pixels"] == 4
    assert resumo["min"] == -200.0
    assert resumo["max"] == 300.0
    assert resumo["negatives"] == 1
    assert resumo["zeros"] == 1
    assert resumo["positives"] == 2
    assert resumo["outside_8bit"] == 2


# Entrada colorida


def test_operacoes_aceitam_imagem_colorida():
    colorida = np.zeros((5, 5, 3), dtype=np.uint8)
    colorida[2, 2] = [100, 150, 200]

    result = operations.mean_filter(colorida, 3, operations.BORDER_REPLICATE)

    assert result.ndim == 2
    assert result[2, 2] == pytest.approx(159 / 9)
