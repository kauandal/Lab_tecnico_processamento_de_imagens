# Laboratório M1.3: convolução e filtragem espacial

Laboratório entregue: M1.3 da disciplina Processamento de Imagens, 2026-02.
Linguagem: Python.
Estudante: Kauan Rocha Dalfovo.

## Objetivo

Implementar operações de vizinhança no domínio espacial, tratando
explicitamente kernels, bordas, tipos numéricos e saturação. Cada pixel de
saída depende de uma vizinhança da entrada.

A convolução, o percurso das vizinhanças e o tratamento das bordas são
implementados manualmente. O OpenCV é usado apenas para abrir e salvar
arquivos, e o NumPy apenas para alocar matrizes e acessar pixels.

## Convenção adotada

Os coeficientes do kernel são aplicados na orientação em que estão escritos,
sem giro de 180 graus. Essa é a convenção didática adotada no material da
disciplina. Estritamente, a operação corresponde a uma correlação. Para
kernels simétricos, como média e gaussiano, as duas convenções coincidem. Para
Sobel, o giro inverteria o sinal das respostas, mas não a magnitude das bordas.

## Dependências

- Python 3.10 ou superior, testado em 3.13.14
- numpy 2.5.2
- opencv-python 5.0.0.93
- pytest 9.1.1

As versões estão fixadas em `requirements.txt`.

## Preparação do ambiente

Windows, PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Linux, macOS ou MSYS2 UCRT64:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Instalação do pacote

O código fica em `src/pdi_lab`. Há duas formas de torná-lo executável.

Forma 1, instalação em modo editável:

```bash
python -m pip install -e .
python -m pdi_lab --help
```

Forma 2, sem instalar, apontando o `PYTHONPATH` para `src`:

```bash
PYTHONPATH=src python -m pdi_lab --help
```

No PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m pdi_lab --help
```

O script `lab_3_m1.py` na raiz não exige nenhuma das duas formas, porque
resolve o caminho de `src` sozinho.

## Execução

### Reproduzir todas as saídas de uma vez

```bash
python lab_3_m1.py
```

Lê `images/input/aura.png`, gera as imagens sintéticas de teste, grava 25
imagens em `images/output/` e as respostas brutas, os perfis de borda e o
resumo estatístico em `results/`. A execução leva cerca de 4,4 segundos.

### Executar uma operação isolada

Forma geral:

```bash
python -m pdi_lab --input <arquivo> --output <arquivo-ou-diretorio> --operation <operacao> [parametros]
```

| Operação | Parâmetros | Resultado |
|---|---|---|
| `convolution` | `--kernel arquivo`, `--border`, `--scale` | resposta do kernel informado |
| `mean_filter` | `--size N`, `--border` | média com janela N por N |
| `weighted_mean` | `--border` | média ponderada 3 por 3 |
| `laplacian` | `--border`, `--view` | resposta do Laplaciano |
| `laplacian_enhance` | `--border`, `--alpha` | imagem realçada |
| `sobel` | `--border`, `--component`, `--view` | `gx`, `gy`, `l1` ou `l2` |
| `grayscale_weighted` | nenhum | imagem base em níveis de cinza |

`--border` aceita `copy` ou `replicate`, com padrão `replicate`.

## Modos de visualização

As respostas de kernels derivativos não cabem em 8 bits. O parâmetro `--view`
escolhe como convertê-las para imagem:

| Modo | Transformação | Uso |
|---|---|---|
| `clamp` | arredonda e satura em 0 e 255 | preserva a escala absoluta |
| `abs` | valor absoluto e depois satura | mostra a força, descarta o sinal |
| `offset` | soma 128 e satura | 128 representa resposta zero |
| `normalize` | mapeia a faixa observada para 0 a 255 | melhora a visibilidade, altera a escala |

O padrão depende da operação: `offset` para Laplaciano e para as componentes
`gx` e `gy`, e `clamp` para as demais. A transformação usada é impressa na
saída padrão a cada execução.

Para preservar a resposta antes da conversão, use `--raw-output`, que grava a
matriz em CSV sem saturar nem arredondar:

```bash
python -m pdi_lab --input images/input/step_vertical.png --output images/output/lap.png --operation laplacian --raw-output results/lap_raw.csv
```

## Exemplos de comandos

Convolução genérica com kernel identidade:

```bash
python -m pdi_lab --input images/input/aura.png --output images/output/identity_replicate.png --operation convolution --kernel kernels/identity_3x3.txt --border replicate
```

Filtros de suavização:

```bash
python -m pdi_lab --input images/input/aura.png --output images/output/mean_3x3_replicate.png --operation mean_filter --size 3
python -m pdi_lab --input images/input/aura.png --output images/output/mean_5x5_replicate.png --operation mean_filter --size 5
python -m pdi_lab --input images/input/aura.png --output images/output/weighted_mean_3x3_replicate.png --operation weighted_mean
```

Comparação das estratégias de borda:

```bash
python -m pdi_lab --input images/input/shapes.png --output images/output --operation mean_filter --size 3 --border copy
python -m pdi_lab --input images/input/shapes.png --output images/output --operation mean_filter --size 3 --border replicate
```

Laplaciano e realce:

```bash
python -m pdi_lab --input images/input/aura.png --output images/output/laplacian_offset_replicate.png --operation laplacian --view offset
python -m pdi_lab --input images/input/aura.png --output images/output/laplacian_enhance_replicate.png --operation laplacian_enhance --alpha 1.0
```

Sobel, as quatro saídas:

```bash
python -m pdi_lab --input images/input/aura.png --output images/output/sobel_gx_replicate.png --operation sobel --component gx
python -m pdi_lab --input images/input/aura.png --output images/output/sobel_gy_replicate.png --operation sobel --component gy
python -m pdi_lab --input images/input/aura.png --output images/output/sobel_l1_replicate.png --operation sobel --component l1
python -m pdi_lab --input images/input/aura.png --output images/output/sobel_l2_replicate.png --operation sobel --component l2
```

Quando `--output` aponta para um diretório, o nome do arquivo é gerado a partir
da operação, dos parâmetros e da estratégia de borda, por exemplo
`mean_3x3_copy.png`.

## Formato dos kernels

A primeira linha traz o número de linhas e de colunas. As linhas seguintes
trazem os coeficientes.

```text
3 3
0 0 0
0 1 0
0 0 0
```

O programa valida existência do arquivo, cabeçalho, quantidade de valores,
formato quadrado e dimensão ímpar.

Kernels versionados em `kernels/`:

| Arquivo | Conteúdo |
|---|---|
| `identity_3x3.txt` | identidade |
| `mean_3x3.txt`, `mean_5x5.txt` | média, coeficientes iguais a 1 |
| `gaussian_3x3.txt` | aproximação gaussiana `[1 2 1; 2 4 2; 1 2 1]` |
| `laplacian_3x3.txt`, `laplacian8_3x3.txt` | Laplaciano de 4 e de 8 vizinhos |
| `sharpen_3x3.txt` | realce equivalente a `f - L` |
| `sobel_x_3x3.txt`, `sobel_y_3x3.txt` | componentes do gradiente |

Os arquivos de média trazem coeficientes iguais a 1, sem normalização, como
fornecido pela disciplina. A operação `convolution` aplica o kernel exatamente
como está no arquivo, então usá-lo direto produz uma resposta nove vezes maior
que a média. Para obter a média, use `mean_filter`, que normaliza internamente,
ou informe `--scale 0.111111`.

## Códigos de saída

| Código | Significado |
|---:|---|
| 0 | operação concluída |
| 1 | erro previsto, com mensagem explicativa em `stderr` |
| 2 | erro de uso dos argumentos |

## Testes

```bash
python -m pytest
```

São 92 testes, divididos em quatro arquivos:

- `tests/test_operations.py`, corretude das operações de vizinhança com imagens
  sintéticas previsíveis, comparação entre as estratégias de borda, valores do
  material conferidos à mão e modos de visualização;
- `tests/test_kernels.py`, leitura e validação dos kernels, incluindo todos os
  casos de arquivo inválido;
- `tests/test_cli.py`, interface de linha de comando e códigos de saída;
- `tests/test_structure.py`, estrutura de entrega e validade do `lab.json`.

## Estrutura do projeto

```text
Lab_tecnico_3_M1_processamento_de_imagens/
├── README.md
├── REPORT.md
├── AI_USAGE.md
├── lab.json
├── requirements.txt
├── pyproject.toml
├── conftest.py
├── lab_3_m1.py                 reprodução de todas as saídas
├── laboratorio_M1_3.md         enunciado do laboratório
├── bordas.md                   material de apoio sobre replicate
├── filtro_laplaciano.md        material de apoio
├── filtro_sobel.md             material de apoio
├── encontro_04_dominio_espacial.md
├── src/
│   └── pdi_lab/
│       ├── __init__.py
│       ├── __main__.py         permite python -m pdi_lab
│       ├── cli.py              argumentos, despacho e códigos de saída
│       ├── errors.py           erro de domínio
│       ├── image_io.py         leitura e escrita, com guardas
│       ├── kernels.py          leitura, validação e kernels embutidos
│       └── operations.py       operações implementadas manualmente
├── tests/
├── kernels/
├── images/
│   ├── input/                  aura.png e as quatro imagens sintéticas
│   └── output/                 imagens geradas
└── results/                    respostas brutas, perfis de borda e resumo
```

## Imagens de entrada

- `images/input/aura.png`, 638 por 480, imagem real usada nos resultados;
- `images/input/step_vertical.png`, degrau vertical 16 por 16;
- `images/input/step_horizontal.png`, degrau horizontal 16 por 16;
- `images/input/impulse.png`, um único pixel de valor 255 no centro;
- `images/input/shapes.png`, formas simples com conteúdo encostado nas bordas
  esquerda e superior, usada para comparar `copy` e `replicate`.

As quatro sintéticas são geradas pelo próprio `lab_3_m1.py` e permitem prever o
resultado antes de executar.

## Arquivos em results

| Arquivo | Conteúdo |
|---|---|
| `summary.csv` | estatísticas de cada resposta bruta |
| `border_profile_mean_3.csv`, `border_profile_mean_5.csv` | diferença entre `copy` e `replicate` por distância até a borda |
| `raw_impulse_mean_3x3.csv` | resposta ao impulso, sem saturar |
| `raw_step_vertical_gx.csv`, `raw_step_vertical_gy.csv` | componentes do gradiente no degrau vertical |
| `raw_step_horizontal_gx.csv`, `raw_step_horizontal_gy.csv` | o mesmo para o degrau horizontal |
| `raw_step_vertical_laplacian.csv` | resposta do Laplaciano no degrau |
| `execucao.log` | registro da execução completa |
