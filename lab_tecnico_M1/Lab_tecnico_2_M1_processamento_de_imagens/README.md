# Laboratório M1.2: transformações de intensidade

Laboratório entregue: M1.2 da disciplina Processamento de Imagens, 2026-02.
Linguagem: Python.
Estudante: Kauan Rocha Dalfovo.

## Objetivo

Implementar manualmente transformações pontuais sobre imagens em níveis de
cinza: brilho, contraste, negativo, limiarização binária e histograma. Cada
pixel de saída depende apenas do pixel correspondente da entrada.

Todas as operações avaliadas percorrem os pixels explicitamente. O OpenCV é
usado apenas para abrir e salvar arquivos, e o NumPy apenas para alocar
matrizes e acessar pixels.

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

O script `lab_2_m1.py` na raiz não exige nenhuma das duas formas, porque
resolve o caminho de `src` sozinho.

## Execução

### Reproduzir todas as saídas de uma vez

```bash
python lab_2_m1.py
```

Lê `images/input/aura.png`, grava nove imagens em `images/output/`, dez
histogramas em CSV e o resumo estatístico em `results/`. A execução leva cerca
de 1,3 segundo.

Para usar outra imagem:

```bash
python lab_2_m1.py --input images/input/ramp.png
```

### Executar uma operação isolada

Forma geral:

```bash
python -m pdi_lab --input <arquivo> --output <arquivo-ou-diretorio> --operation <operacao> [parametros]
```

| Operação | Parâmetro obrigatório | Saída |
|---|---|---|
| `brightness` | `--value N`, positivo ou negativo | imagem |
| `contrast` | `--alpha F`, maior ou igual a zero | imagem |
| `negative` | nenhum | imagem |
| `threshold` | `--threshold N`, de 0 a 255 | imagem |
| `histogram` | nenhum | CSV |
| `grayscale_weighted` | nenhum | imagem |

A operação `grayscale_weighted` é auxiliar, usada para produzir a imagem base
em níveis de cinza. As demais aceitam entrada colorida e aplicam essa mesma
conversão antes de transformar.

## Exemplos de comandos

Base em níveis de cinza:

```bash
python -m pdi_lab --input images/input/aura.png --output images/output/gray_weighted.png --operation grayscale_weighted
```

Brilho, um teste positivo e um negativo:

```bash
python -m pdi_lab --input images/output/gray_weighted.png --output images/output/brightness_pos50.png --operation brightness --value 50
python -m pdi_lab --input images/output/gray_weighted.png --output images/output/brightness_neg50.png --operation brightness --value -50
```

Contraste, com os três fatores pedidos:

```bash
python -m pdi_lab --input images/output/gray_weighted.png --output images/output/contrast_0_5.png --operation contrast --alpha 0.5
python -m pdi_lab --input images/output/gray_weighted.png --output images/output/contrast_1_0.png --operation contrast --alpha 1.0
python -m pdi_lab --input images/output/gray_weighted.png --output images/output/contrast_1_5.png --operation contrast --alpha 1.5
```

Negativo:

```bash
python -m pdi_lab --input images/output/gray_weighted.png --output images/output/negative.png --operation negative
```

Limiarização, com dois limiares distintos:

```bash
python -m pdi_lab --input images/output/gray_weighted.png --output images/output/threshold_128.png --operation threshold --threshold 128
python -m pdi_lab --input images/output/gray_weighted.png --output images/output/threshold_64.png --operation threshold --threshold 64
```

Histograma em CSV:

```bash
python -m pdi_lab --input images/output/gray_weighted.png --output results/histogram_original.csv --operation histogram
```

Quando `--output` aponta para um diretório, o nome do arquivo é gerado a partir
da operação e do parâmetro. O comando abaixo cria
`images/output/threshold_128.png`:

```bash
python -m pdi_lab --input images/output/gray_weighted.png --output images/output --operation threshold --threshold 128
```

## Formato do histograma

CSV com cabeçalho e 256 linhas de dados, conforme o contrato técnico:

```text
intensity,count
0,51
1,336
...
255,0
```

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

São 60 testes, divididos em três arquivos:

- `tests/test_operations.py`, corretude das transformações com imagem
  sintética conferível à mão, casos de saturação, identidades matemáticas e
  guardas;
- `tests/test_cli.py`, interface de linha de comando, formato do CSV e códigos
  de saída;
- `tests/test_structure.py`, estrutura de entrega e validade do `lab.json`.

## Estrutura do projeto

```text
Lab_tecnico_2_M1_processamento_de_imagens/
├── README.md
├── REPORT.md
├── AI_USAGE.md
├── lab.json
├── requirements.txt
├── pyproject.toml
├── conftest.py
├── lab_2_m1.py            reprodução de todas as saídas
├── laboratorio_M1_2.md    enunciado do laboratório
├── mural.md               relato da evidência parcial
├── src/
│   └── pdi_lab/
│       ├── __init__.py
│       ├── __main__.py    permite python -m pdi_lab
│       ├── cli.py         argumentos, despacho e códigos de saída
│       ├── errors.py      erro de domínio
│       ├── image_io.py    leitura e escrita, com guardas
│       └── operations.py  transformações implementadas manualmente
├── tests/
├── kernels/               vazio neste laboratório, usado a partir do M1.3
├── images/
│   ├── input/             aura.png e ramp.png
│   └── output/            imagens geradas
└── results/               histogramas em CSV e summary.csv
```

## Imagens de entrada

- `images/input/aura.png`, 638 x 480, imagem real usada nos resultados;
- `images/input/ramp.png`, 256 x 64, rampa sintética com exatamente 64 pixels
  em cada intensidade de 0 a 255. O histograma uniforme dessa imagem permite
  conferir à mão o efeito de cada transformação sobre a distribuição. Ela é
  gerada pelo próprio `lab_2_m1.py`.
