"""Leitura, validação e definição dos kernels usados no laboratório M1.3.

O formato de arquivo é o definido pelo contrato técnico: a primeira linha traz
o número de linhas e de colunas, e as linhas seguintes trazem os coeficientes.

::

    3 3
    0 0 0
    0 1 0
    0 0 0
"""

from __future__ import annotations

from pathlib import Path

from .errors import PdiLabError

# Kernels usados pelas operações nomeadas, na convenção do material da
# disciplina: os coeficientes são aplicados na orientação em que estão
# escritos, sem giro de 180 graus.
IDENTITY_3X3 = [
    [0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0],
    [0.0, 0.0, 0.0],
]

# Aproximação gaussiana 3x3. O fator 1/16 é a soma dos coeficientes.
WEIGHTED_MEAN_3X3 = [
    [1.0, 2.0, 1.0],
    [2.0, 4.0, 2.0],
    [1.0, 2.0, 1.0],
]

# Laplaciano de 4 vizinhos, com centro negativo. Resposta positiva quando o
# centro é mais escuro que a vizinhança.
LAPLACIAN_3X3 = [
    [0.0, 1.0, 0.0],
    [1.0, -4.0, 1.0],
    [0.0, 1.0, 0.0],
]

# Laplaciano de 8 vizinhos, incluindo as diagonais.
LAPLACIAN8_3X3 = [
    [1.0, 1.0, 1.0],
    [1.0, -8.0, 1.0],
    [1.0, 1.0, 1.0],
]

SOBEL_X_3X3 = [
    [-1.0, 0.0, 1.0],
    [-2.0, 0.0, 2.0],
    [-1.0, 0.0, 1.0],
]

SOBEL_Y_3X3 = [
    [-1.0, -2.0, -1.0],
    [0.0, 0.0, 0.0],
    [1.0, 2.0, 1.0],
]


def validate_kernel(kernel: list[list[float]]) -> None:
    """Verifica as pré-condições de um kernel.

    Exige matriz não vazia, retangular, quadrada e de dimensão ímpar, para que
    exista um centro bem definido.
    """
    if not kernel or not kernel[0]:
        raise PdiLabError("kernel vazio")

    rows = len(kernel)
    columns = len(kernel[0])

    for row in kernel:
        if len(row) != columns:
            raise PdiLabError("kernel com linhas de tamanhos diferentes")

    if rows != columns:
        raise PdiLabError(
            "kernel deve ser quadrado; recebido "
            + str(rows)
            + "x"
            + str(columns)
        )
    if rows % 2 == 0:
        raise PdiLabError(
            "kernel deve ter dimensao impar; recebido " + str(rows)
        )


def mean_kernel(size: int) -> list[list[float]]:
    """Kernel de média com ``size`` por ``size`` posições, já normalizado.

    Cada coeficiente vale ``1 / (size * size)``, de forma que a soma seja 1 e
    uma região constante seja preservada.
    """
    if isinstance(size, bool) or not isinstance(size, int):
        raise PdiLabError("tamanho de kernel invalido: " + repr(size))
    if size < 1:
        raise PdiLabError(
            "tamanho de kernel invalido: " + str(size) + "; use um inteiro impar positivo"
        )
    if size % 2 == 0:
        raise PdiLabError(
            "tamanho de kernel invalido: " + str(size) + "; use um inteiro impar"
        )

    weight = 1.0 / (size * size)
    return [[weight] * size for _ in range(size)]


def normalized(kernel: list[list[float]]) -> list[list[float]]:
    """Divide o kernel pela soma dos coeficientes, quando ela não é zero.

    Kernels de suavização devem somar 1 para preservar o nível médio. Kernels
    derivativos somam zero e são devolvidos sem alteração.
    """
    validate_kernel(kernel)

    total = sum(sum(row) for row in kernel)
    if total == 0:
        return [list(row) for row in kernel]
    return [[value / total for value in row] for row in kernel]


def load_kernel(path: str | Path) -> list[list[float]]:
    """Carrega um kernel de arquivo no formato do contrato técnico."""
    path = Path(path)

    if not path.exists():
        raise PdiLabError("arquivo de kernel nao encontrado: " + str(path))
    if not path.is_file():
        raise PdiLabError("caminho de kernel nao e um arquivo: " + str(path))

    text = path.read_text(encoding="utf-8")
    tokens = text.split()
    if not tokens:
        raise PdiLabError("arquivo de kernel vazio: " + str(path))
    if len(tokens) < 2:
        raise PdiLabError(
            "cabecalho do kernel incompleto; esperado numero de linhas e colunas"
        )

    try:
        rows = int(tokens[0])
        columns = int(tokens[1])
    except ValueError:
        raise PdiLabError(
            "cabecalho do kernel invalido: esperado dois inteiros, recebido "
            + " ".join(tokens[:2])
        ) from None

    if rows <= 0 or columns <= 0:
        raise PdiLabError(
            "dimensoes do kernel devem ser positivas; recebido "
            + str(rows)
            + "x"
            + str(columns)
        )

    values = tokens[2:]
    expected = rows * columns
    if len(values) != expected:
        raise PdiLabError(
            "quantidade de valores do kernel nao confere; esperado "
            + str(expected)
            + ", encontrado "
            + str(len(values))
        )

    try:
        numbers = [float(value) for value in values]
    except ValueError:
        raise PdiLabError(
            "kernel contem valor nao numerico em " + str(path)
        ) from None

    kernel = [
        numbers[index * columns : (index + 1) * columns] for index in range(rows)
    ]
    validate_kernel(kernel)
    return kernel
