"""Testes de leitura e validação de kernels."""

from pathlib import Path

import pytest

from pdi_lab import kernels
from pdi_lab.errors import PdiLabError

# Os kernels versionados do projeto, independentes do diretorio de trabalho.
PROJECT_KERNELS = Path(__file__).resolve().parent.parent / "kernels"


def write_kernel(tmp_path, content, name="k.txt"):
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def test_le_kernel_identidade_do_projeto():
    kernel = kernels.load_kernel(PROJECT_KERNELS / "identity_3x3.txt")

    assert kernel == [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]]


def test_le_kernel_5x5_do_projeto():
    kernel = kernels.load_kernel(PROJECT_KERNELS / "mean_5x5.txt")

    assert len(kernel) == 5
    assert all(len(row) == 5 for row in kernel)


def test_le_kernel_com_valores_negativos_e_decimais(tmp_path):
    path = write_kernel(tmp_path, "3 3\n-1 0 1\n-2.5 0 2.5\n-1 0 1\n")

    kernel = kernels.load_kernel(path)

    assert kernel[1] == [-2.5, 0.0, 2.5]


def test_arquivo_de_kernel_inexistente(tmp_path):
    with pytest.raises(PdiLabError, match="nao encontrado"):
        kernels.load_kernel(tmp_path / "nao_existe.txt")


def test_arquivo_de_kernel_vazio(tmp_path):
    with pytest.raises(PdiLabError, match="vazio"):
        kernels.load_kernel(write_kernel(tmp_path, ""))


def test_cabecalho_incompleto(tmp_path):
    with pytest.raises(PdiLabError, match="cabecalho"):
        kernels.load_kernel(write_kernel(tmp_path, "3\n"))


def test_cabecalho_nao_numerico(tmp_path):
    with pytest.raises(PdiLabError, match="cabecalho"):
        kernels.load_kernel(write_kernel(tmp_path, "tres tres\n1 1 1\n"))


def test_quantidade_de_valores_incorreta(tmp_path):
    with pytest.raises(PdiLabError, match="quantidade"):
        kernels.load_kernel(write_kernel(tmp_path, "3 3\n1 1 1\n1 1 1\n"))


def test_kernel_nao_quadrado(tmp_path):
    with pytest.raises(PdiLabError, match="quadrado"):
        kernels.load_kernel(write_kernel(tmp_path, "1 3\n1 1 1\n"))


def test_kernel_de_dimensao_par(tmp_path):
    with pytest.raises(PdiLabError, match="impar"):
        kernels.load_kernel(write_kernel(tmp_path, "2 2\n1 1\n1 1\n"))


def test_kernel_com_valor_nao_numerico(tmp_path):
    with pytest.raises(PdiLabError, match="nao numerico"):
        kernels.load_kernel(write_kernel(tmp_path, "3 3\n1 1 1\n1 x 1\n1 1 1\n"))


def test_dimensoes_negativas(tmp_path):
    with pytest.raises(PdiLabError, match="positivas"):
        kernels.load_kernel(write_kernel(tmp_path, "-3 -3\n1\n"))


def test_validacao_recusa_kernel_vazio():
    with pytest.raises(PdiLabError, match="vazio"):
        kernels.validate_kernel([])
    with pytest.raises(PdiLabError, match="vazio"):
        kernels.validate_kernel([[]])


def test_validacao_recusa_linhas_de_tamanhos_diferentes():
    with pytest.raises(PdiLabError, match="tamanhos diferentes"):
        kernels.validate_kernel([[1, 2, 3], [1, 2]])


def test_kernel_de_media_esta_normalizado():
    kernel = kernels.mean_kernel(3)

    assert len(kernel) == 3
    assert sum(sum(row) for row in kernel) == pytest.approx(1.0)
    assert kernel[0][0] == pytest.approx(1 / 9)


@pytest.mark.parametrize("size", [0, -1, 2, 4, 2.5, "3"])
def test_tamanho_invalido_de_media(size):
    with pytest.raises(PdiLabError):
        kernels.mean_kernel(size)


def test_normalizacao_divide_pela_soma():
    kernel = kernels.normalized(kernels.WEIGHTED_MEAN_3X3)

    assert sum(sum(row) for row in kernel) == pytest.approx(1.0)
    assert kernel[1][1] == pytest.approx(4 / 16)
    assert kernel[0][0] == pytest.approx(1 / 16)


def test_normalizacao_preserva_kernel_de_soma_zero():
    """Kernels derivativos somam zero e nao devem ser divididos."""
    kernel = kernels.normalized(kernels.LAPLACIAN_3X3)

    assert kernel == kernels.LAPLACIAN_3X3


def test_kernels_derivativos_somam_zero():
    for kernel in (
        kernels.LAPLACIAN_3X3,
        kernels.LAPLACIAN8_3X3,
        kernels.SOBEL_X_3X3,
        kernels.SOBEL_Y_3X3,
    ):
        assert sum(sum(row) for row in kernel) == 0
