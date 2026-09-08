# Laboratório M1.1: representação, canais e níveis de cinza

Laboratório entregue: M1.1 da disciplina Processamento de Imagens, 2026-02.
Linguagem: Python.
Estudante: Kauan Rocha Dalfovo.

## Objetivo

Implementar manualmente as operações fundamentais de representação de imagens
digitais: inspeção, cópia, separação de canais, conversão para níveis de cinza
pelas duas fórmulas e quantização.

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

O código fica em `src/pdi_lab`. Há duas formas de torná-lo executável, ambas
válidas.

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

O script `lab_1_m1.py` na raiz não exige nenhuma das duas formas, porque
resolve o caminho de `src` sozinho.

## Execução

### Reproduzir todas as saídas de uma vez

```bash
python lab_1_m1.py
```

Lê `images/input/aura_small.png`, grava as dez imagens em `images/output/` e a
inspeção em `results/inspect.txt`. A execução leva cerca de 1 segundo.

Para usar outra imagem:

```bash
python lab_1_m1.py --input images/input/aura.png --output-dir images/output
```

### Executar uma operação isolada

Forma geral:

```bash
python -m pdi_lab --input <arquivo> --output <arquivo-ou-diretorio> --operation <operacao> [--levels N]
```

Operações disponíveis: `inspect`, `copy`, `channel_b`, `channel_g`,
`channel_r`, `grayscale_average`, `grayscale_weighted`, `quantize`.

## Exemplos de comandos

Inspeção, que escreve na saída padrão:

```bash
python -m pdi_lab --input images/input/aura_small.png --operation inspect
```

Inspeção gravando também em arquivo:

```bash
python -m pdi_lab --input images/input/aura_small.png --output results/inspect.txt --operation inspect
```

Cópia manual:

```bash
python -m pdi_lab --input images/input/aura_small.png --output images/output/copy.png --operation copy
```

Canal azul, verde e vermelho:

```bash
python -m pdi_lab --input images/input/aura_small.png --output images/output/channel_b.png --operation channel_b
python -m pdi_lab --input images/input/aura_small.png --output images/output/channel_g.png --operation channel_g
python -m pdi_lab --input images/input/aura_small.png --output images/output/channel_r.png --operation channel_r
```

Níveis de cinza pelas duas fórmulas:

```bash
python -m pdi_lab --input images/input/aura_small.png --output images/output/gray_average.png --operation grayscale_average
python -m pdi_lab --input images/input/aura_small.png --output images/output/gray_weighted.png --operation grayscale_weighted
```

Quantização:

```bash
python -m pdi_lab --input images/output/gray_weighted.png --output images/output/quant_16.png --operation quantize --levels 16
python -m pdi_lab --input images/output/gray_weighted.png --output images/output/quant_8.png --operation quantize --levels 8
python -m pdi_lab --input images/output/gray_weighted.png --output images/output/quant_4.png --operation quantize --levels 4
python -m pdi_lab --input images/output/gray_weighted.png --output images/output/quant_2.png --operation quantize --levels 2
```

Quando `--output` aponta para um diretório, o nome do arquivo é gerado a partir
da operação. O comando abaixo cria `images/output/quant_8.png`:

```bash
python -m pdi_lab --input images/input/aura_small.png --output images/output --operation quantize --levels 8
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

São 44 testes, divididos em três arquivos:

- `tests/test_operations.py`, corretude das operações com imagens sintéticas
  conferíveis à mão, além dos casos de borda e das guardas;
- `tests/test_cli.py`, interface de linha de comando, arquivos gerados e
  códigos de saída;
- `tests/test_structure.py`, estrutura de entrega e validade do `lab.json`.

O arquivo `conftest.py` coloca `src` no caminho de importação, então os testes
rodam sem instalação prévia do pacote.

## Estrutura do projeto

```text
Lab_tecnico_1_M1_processamento_de_imagens/
├── README.md
├── REPORT.md
├── AI_USAGE.md
├── lab.json
├── requirements.txt
├── pyproject.toml
├── conftest.py
├── lab_1_m1.py            reprodução de todas as saídas
├── lab_1_m1.md            enunciado do laboratório
├── src/
│   └── pdi_lab/
│       ├── __init__.py
│       ├── __main__.py    permite python -m pdi_lab
│       ├── cli.py         argumentos, despacho e códigos de saída
│       ├── errors.py      erro de domínio
│       ├── image_io.py    leitura e escrita, com guardas
│       └── operations.py  operações implementadas manualmente
├── tests/
├── kernels/               vazio neste laboratório, usado a partir do M1.3
├── images/
│   ├── input/             aura.png e aura_small.png
│   └── output/            imagens geradas
└── results/               inspect.txt
```

## Imagens de entrada

- `images/input/aura.png`, imagem original, 6960 x 4640, 32,3 megapixels;
- `images/input/aura_small.png`, mesma cena em 638 x 480.

As saídas versionadas foram geradas a partir da versão menor. O motivo é
prático: como o percurso dos pixels é explícito, sem vetorização, a imagem de
32 megapixels leva cerca de 9 minutos para gerar o conjunto completo, contra
1 segundo da versão menor. A imagem original é aceita normalmente pelos mesmos
comandos.

## Convenções de nomes das saídas

Os nomes seguem a sugestão do enunciado. A única diferença é que a conversão
ponderada é gravada como `gray_weighted.png`, com sublinhado, e não
`gray.weighted.png`.
