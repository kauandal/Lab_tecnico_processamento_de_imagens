# Laboratório M2.2: componentes conexos e sequência morfológica

Laboratório entregue: M2.2 da disciplina Processamento de Imagens, 2026-02,
na entrega consolidada com o M2.1.
Linguagem: Python.
Estudante: Kauan Rocha Dalfovo.

## Objetivo

Ampliar o projeto do M2.1 para limpar a máscara de moedas com uma sequência
morfológica, rotular os componentes conexos e contar os objetos antes e
depois da limpeza. A operação `segment` do M2.1 continua funcionando no
mesmo pacote, e a nova operação é `analyze`.

Na M2 as funções do OpenCV podem ser usadas para limiarização, morfologia e
rotulação. O contrato complementar da M2 ainda não foi publicado, então o
projeto segue o contrato técnico da M1, com as adaptações dos enunciados da
M2.

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

Os scripts `lab_1_m2.py` e `lab_2_m2.py` na raiz não exigem nenhuma das duas
formas, porque resolvem o caminho de `src` sozinhos.

## Execução

### Reproduzir todas as saídas de uma vez

M2.1, máscaras:

```bash
python lab_1_m2.py
```

Processa `coins.png` e `moedas_real_separadas.jpg` com o limiar fixo e com o
Otsu, e a foto colorida também com HSV. Grava as máscaras, as sobreposições e
as figuras de comparação em `images/output/` e as tabelas em `results/`.

M2.2, componentes e morfologia:

```bash
python lab_2_m2.py
```

Refaz as máscaras do M2.1, gera a máscara de `moedas_real_empilhadas.jpg` e
executa `analyze` sobre as três máscaras. Grava os estágios, os CSV, as
imagens de rótulos e os resumos em `results/`, as figuras dos estágios em
`images/output/` e a tabela antes e depois em `results/comparison.csv`. A
execução leva cerca de 5 segundos.

### Executar uma operação isolada

Segmentação, do M2.1:

```bash
python -m pdi_lab --input <imagem> --output <mascara.png> --operation segment --method <metodo> [parametros]
```

Análise, do M2.2:

```bash
python -m pdi_lab --input <mascara.png> --output <prefixo> --operation analyze --sequence <config.json> [--connectivity 4|8] [--min-area N]
```

Parâmetros de `segment`:

| Método | Parâmetros | Regra |
|---|---|---|
| `fixed` | `--threshold T`, obrigatório, de 0 a 255 | objeto onde cinza > T |
| `otsu` | nenhum | limiar calculado pelo Otsu, impresso como `otsu_threshold` |
| `adaptive` | `--block-size N`, ímpar >= 3, padrão 31; `--c C`, obrigatório; `--adaptive-kind mean` ou `gaussian`, padrão `gaussian` | objeto onde pixel > média local - C |
| `hsv` | `--hsv-lower H,S,V` e `--hsv-upper H,S,V`, obrigatórios | objeto dentro do intervalo, com H de 0 a 179 e S e V de 0 a 255 |

Valem para todos os métodos: `--blur N`, suavização gaussiana antes do método,
com 0 desligando; `--invert`, para objeto mais escuro que o fundo; e
`--overlay arquivo`, que grava a original com a moeda em verde e o contorno em
vermelho. A máscara usa 255 para moeda e 0 para fundo, e só são aceitos
formatos sem perdas na saída da máscara.

Parâmetros de `analyze`:

| Parâmetro | Efeito |
|---|---|
| `--input` | máscara binária, um canal, valores só em {0, 255} |
| `--output` | prefixo dos arquivos gerados, por exemplo `results/coins` |
| `--sequence` | arquivo JSON com a sequência morfológica, obrigatório |
| `--connectivity` | 4 ou 8, padrão 8; é a conectividade dos CSV e da imagem de rótulos |
| `--min-area` | área mínima, em pixels, para manter um componente; inteiro não negativo, padrão 0 |

A máscara inicial e a final são sempre contadas nas duas conectividades, com
os mesmos parâmetros, e as contagens aparecem na saída padrão e no resumo. O
fundo, rótulo 0, nunca entra na contagem nem nos CSV.

## Formato da sequência morfológica

A sequência fica num arquivo JSON em `config/`, então outro caso pode ser
reproduzido sem editar o código:

```json
{
  "steps": [
    {"operation": "open", "shape": "ellipse", "size": 3, "iterations": 1,
     "purpose": "remover pontos isolados de fundo"},
    {"operation": "close", "shape": "ellipse", "size": 7, "iterations": 1,
     "purpose": "fechar furos pequenos dentro das moedas"}
  ]
}
```

| Campo | Valores |
|---|---|
| `operation` | `erode`, `dilate`, `open` ou `close` |
| `shape` | `rect`, `ellipse` ou `cross` |
| `size` | lado do elemento estruturante, inteiro ímpar >= 3 |
| `iterations` | inteiro >= 1, padrão 1 |
| `purpose` | texto obrigatório com o defeito que o passo trata |

O programa recusa sequência com menos de duas operações, sem abertura nem
fechamento, ou com dois passos seguidos idênticos.

Arquivos versionados em `config/`:

| Arquivo | Usado em | Conteúdo |
|---|---|---|
| `coins.json` | `coins.png`, 384 x 303 | abertura elíptica 3 x 3 e fechamento elíptico 7 x 7 |
| `moedas_real.json` | as duas fotos, 3664 x 2748 | abertura elíptica 7 x 7 e fechamento elíptico 41 x 41 |

Os elementos das fotos são maiores porque a resolução é cerca de 90 vezes
maior, e os pontos de ruído e os furos também são maiores em pixels.

## Exemplos de comandos

Máscaras:

```bash
python -m pdi_lab --input images/input/coins.png --output images/output/coins_mask.png --operation segment --method fixed --threshold 120
python -m pdi_lab --input images/input/moedas_real_separadas.jpg --output images/output/moedas_real_separadas_mask.png --operation segment --method hsv --hsv-lower 0,30,0 --hsv-upper 179,255,255 --blur 5
python -m pdi_lab --input images/input/moedas_real_empilhadas.jpg --output images/output/moedas_real_empilhadas_mask.png --operation segment --method otsu --invert --blur 5
```

Análises do M2.2:

```bash
python -m pdi_lab --input images/output/coins_mask.png --output results/coins --operation analyze --sequence config/coins.json --connectivity 8 --min-area 500
python -m pdi_lab --input images/output/moedas_real_separadas_mask.png --output results/moedas_real_separadas --operation analyze --sequence config/moedas_real.json --connectivity 8 --min-area 50000
python -m pdi_lab --input images/output/moedas_real_empilhadas_mask.png --output results/moedas_real_empilhadas --operation analyze --sequence config/moedas_real.json --connectivity 8 --min-area 50000
```

As configurações de comparação do M2.1, com limiar fixo e Otsu, estão no
`lab_1_m2.py`.

## Códigos de saída

| Código | Significado |
|---:|---|
| 0 | operação concluída |
| 1 | erro previsto, com mensagem explicativa em `stderr` |
| 2 | erro de uso dos argumentos, como método, operação ou conectividade inválidos |

## Testes

```bash
python -m pytest
```

São 111 testes, divididos em seis arquivos:

- `tests/test_segmentation.py`, métodos de segmentação do M2.1 com imagens
  sintéticas, validação da máscara e guardas;
- `tests/test_cli.py`, linha de comando de `segment` e códigos de saída;
- `tests/test_real_images.py`, as duas imagens do M2.1 em todas as
  configurações do estudo;
- `tests/test_analysis.py`, conectividade, morfologia, sequência, filtro por
  área e linha de comando de `analyze`;
- `tests/test_real_analysis.py`, reexecução do M2.2 nas três imagens reais,
  com conferência da soma das áreas;
- `tests/test_structure.py`, estrutura de entrega e validade do `lab.json`.

O arquivo `conftest.py` coloca `src` no caminho de importação, então os testes
rodam sem instalação prévia do pacote.

## Estrutura do projeto

```text
Lab_tecnico_2_M2_processamento_de_imagens/
├── README.md
├── REPORT.md
├── AI_USAGE.md
├── lab.json
├── requirements.txt
├── pyproject.toml
├── conftest.py
├── lab_1_m2.py              reprodução das saídas do M2.1
├── lab_2_m2.py              reprodução das saídas do M2.2
├── laboratorio_1_M2.md      enunciado do M2.1
├── laboratorio_2_M2.md      enunciado do M2.2
├── config/                  sequências morfológicas
├── src/
│   └── pdi_lab/
│       ├── __init__.py
│       ├── __main__.py      permite python -m pdi_lab
│       ├── cli.py           argumentos, despacho e códigos de saída
│       ├── errors.py        erro de domínio
│       ├── image_io.py      leitura e escrita, com guardas
│       ├── segmentation.py  métodos do M2.1, validação e sobreposição
│       └── analysis.py      componentes conexos, morfologia e CSV
├── tests/
├── images/
│   ├── input/               coins.png e as duas fotos de moedas do real
│   └── output/              máscaras, sobreposições e figuras
└── results/                 estágios, CSV, rótulos, resumos e registro
```

## Imagens de entrada

- `images/input/coins.png`, 384 x 303, em cinza. Vem do scikit-image v0.26.0
  e é uma foto de moedas gregas do acervo do Brooklyn Museum, sem restrições
  de copyright conhecidas. Tem 24 moedas e fundo irregular.
- `images/input/moedas_real_separadas.jpg`, 3664 x 2748, colorida. Foto
  "Moedas do Real até 2010.jpg", com 12 moedas separadas sobre fundo claro.
- `images/input/moedas_real_empilhadas.jpg`, 3664 x 2748, colorida. Foto
  "Moedas do Real até 2010 - empilhadas.jpg", com dezenas de moedas em pilhas,
  encostadas e sobrepostas. É a imagem do caso de contato.

As duas fotos são de Anderson Batista Evangelista Lima (MisterSanderson),
publicadas no Wikimedia Commons sob a licença Creative Commons
Atribuição-CompartilhaIgual 2.5 Genérica (CC BY-SA 2.5):

- https://commons.wikimedia.org/wiki/File:Moedas_do_Real_at%C3%A9_2010.jpg
- https://commons.wikimedia.org/wiki/File:Moedas_do_Real_at%C3%A9_2010_-_empilhadas.jpg

Os arquivos foram baixados sem alteração e só renomeados. As máscaras,
sobreposições e figuras derivadas das fotos ficam sob a mesma licença.

## Convenções de nomes das saídas

M2.1, em `images/output/`:

| Arquivo | Conteúdo |
|---|---|
| `<imagem>_mask_<config>.png` | máscara de cada configuração: `fixed`, `otsu` e, na foto colorida, `hsv` |
| `<imagem>_overlay_<config>.jpg` | sobreposição de cada configuração, em JPEG porque é só visualização |
| `<imagem>_mask.png` | máscara escolhida, entrada do M2.2 |
| `<imagem>_comparacao.png` | original, as máscaras de cada configuração e a sobreposição escolhida |

M2.2, com o prefixo informado em `--output`:

| Arquivo | Conteúdo |
|---|---|
| `<prefixo>_initial_mask.png` | cópia da máscara inicial |
| `<prefixo>_initial.csv` | componentes da máscara inicial |
| `<prefixo>_stage_<n>_<operacao>.png` | saída de cada estágio da sequência, na ordem |
| `<prefixo>_final_mask.png` | máscara final, igual ao último estágio |
| `<prefixo>_final.csv` | componentes da máscara final |
| `<prefixo>_labels.png` | rótulos coloridos com caixa verde para mantido e vermelha para filtrado |
| `<prefixo>_summary.json` | conectividade, sequência, contagens em 4 e 8, brutas e filtradas, contagem de cada estágio e áreas antes e depois |
| `images/output/<prefixo>_estagios.png` | máscara inicial, cada estágio e rótulos finais lado a lado |

Os CSV têm as colunas `label,area,x,y,width,height,cx,cy,kept`, em que `kept`
indica se o componente passou no filtro de área.

Tabelas em `results/`:

| Arquivo | Conteúdo |
|---|---|
| `foreground.csv` | proporção de primeiro plano por imagem e configuração, do M2.1 |
| `threshold_sensitivity.csv` | proporção de primeiro plano variando o limiar fixo, do M2.1 |
| `comparison.csv` | contagens e áreas antes e depois de cada análise, do M2.2 |
| `execucao.log` | saída completa dos scripts e dos testes |
