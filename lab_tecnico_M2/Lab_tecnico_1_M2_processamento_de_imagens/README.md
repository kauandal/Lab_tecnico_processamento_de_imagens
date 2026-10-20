# Laboratório M2.1: máscara binária e segmentação

Laboratório entregue: M2.1 da disciplina Processamento de Imagens, 2026-02.
Linguagem: Python.
Estudante: Kauan Rocha Dalfovo.

## Objetivo

Gerar e avaliar uma máscara binária de moedas, comparando um limiar fixo em
cinza com o método de Otsu nas mesmas imagens e, na foto colorida, também com
um intervalo HSV. A máscara escolhida aqui é a entrada do M2.2.

Na M2 as funções do OpenCV podem ser usadas para conversão de cor, suavização
e limiarização. O projeto segue o contrato técnico complementar da M2, em
`lab_tecnico_M2/contrato_tecnico.md`, que adapta o contrato da M1, e a
rubrica da M2, em `lab_tecnico_M2/rubrica_avaliativa.md`.

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

O script `lab_1_m2.py` na raiz não exige nenhuma das duas formas, porque
resolve o caminho de `src` sozinho.

## Execução

### Reproduzir todas as saídas de uma vez

```bash
python lab_1_m2.py
```

Processa as duas imagens de `images/input/` com o limiar fixo e com o Otsu, e
a foto colorida também com HSV. Grava as máscaras, as sobreposições e as
figuras de comparação em `images/output/` e as tabelas em `results/`. A
execução leva cerca de 2 segundos.

### Executar uma operação isolada

Forma geral:

```bash
python -m pdi_lab --input <imagem> --output <mascara.png> --operation segment --method <metodo> [parametros]
```

A máscara usa 255 para moeda e 0 para fundo, tem um canal e o mesmo tamanho
da entrada. Só são aceitos formatos sem perdas na saída: `.png`, `.bmp`,
`.tif` e `.tiff`. Depois de gravar, o programa relê o arquivo e confere
dimensões, canal único e valores em {0, 255}. Quando está tudo certo, imprime
`binary_check=ok`.

| Método | Parâmetros | Regra |
|---|---|---|
| `fixed` | `--threshold T`, obrigatório, de 0 a 255 | objeto onde cinza > T |
| `otsu` | nenhum | limiar calculado pelo Otsu, impresso como `otsu_threshold` |
| `adaptive` | `--block-size N`, ímpar >= 3, padrão 31; `--c C`, obrigatório; `--adaptive-kind mean` ou `gaussian`, padrão `gaussian` | objeto onde pixel > média local - C |
| `hsv` | `--hsv-lower H,S,V` e `--hsv-upper H,S,V`, obrigatórios | objeto dentro do intervalo, com H de 0 a 179 e S e V de 0 a 255 |

Parâmetros que valem para todos os métodos:

| Parâmetro | Efeito |
|---|---|
| `--blur N` | suavização gaussiana N por N antes do método; 0 desliga, que é o padrão |
| `--invert` | inverte a máscara, para objeto mais escuro que o fundo |
| `--overlay arquivo` | grava a imagem original com a moeda em verde e o contorno em vermelho |

No `hsv`, quando o H inferior é maior que o superior, a faixa passa pelo 179 e
volta ao 0, e é tratada como a união das duas partes. No `adaptive`, uma
região plana tem o pixel igual à média local, então com C positivo ela vira
objeto e com C negativo vira fundo.

## Exemplos de comandos

Configurações usadas no estudo:

```bash
python -m pdi_lab --input images/input/coins.png --output images/output/coins_mask_fixed.png --operation segment --method fixed --threshold 120 --overlay images/output/coins_overlay_fixed.png
python -m pdi_lab --input images/input/coins.png --output images/output/coins_mask_otsu.png --operation segment --method otsu --overlay images/output/coins_overlay_otsu.png
python -m pdi_lab --input images/input/moedas_real_separadas.jpg --output images/output/moedas_real_separadas_mask_fixed.png --operation segment --method fixed --threshold 85 --invert
python -m pdi_lab --input images/input/moedas_real_separadas.jpg --output images/output/moedas_real_separadas_mask_otsu.png --operation segment --method otsu --invert
python -m pdi_lab --input images/input/moedas_real_separadas.jpg --output images/output/moedas_real_separadas_mask_hsv.png --operation segment --method hsv --hsv-lower 0,30,0 --hsv-upper 179,255,255 --blur 5
```

Máscaras escolhidas para o M2.2:

```bash
python -m pdi_lab --input images/input/coins.png --output images/output/coins_mask.png --operation segment --method fixed --threshold 120
python -m pdi_lab --input images/input/moedas_real_separadas.jpg --output images/output/moedas_real_separadas_mask.png --operation segment --method hsv --hsv-lower 0,30,0 --hsv-upper 179,255,255 --blur 5
```

Outro método, não usado no estudo:

```bash
python -m pdi_lab --input images/input/coins.png --output images/output/coins_mask_adaptive.png --operation segment --method adaptive --block-size 51 --c -10
```

## Códigos de saída

| Código | Significado |
|---:|---|
| 0 | máscara gerada, gravada e validada |
| 1 | erro previsto, com mensagem explicativa em `stderr`: arquivo ausente ou ilegível, imagem incompatível, parâmetro inválido, máscara não binária ou falha de gravação |
| 2 | erro de uso dos argumentos, como método desconhecido |

## Testes

```bash
python -m pytest
```

São 72 testes, divididos em quatro arquivos:

- `tests/test_segmentation.py`, métodos de segmentação com imagens sintéticas
  conferíveis à mão, validação da máscara e guardas;
- `tests/test_cli.py`, interface de linha de comando, arquivos gerados e
  códigos de saída;
- `tests/test_real_images.py`, as duas imagens reais em todas as
  configurações do estudo;
- `tests/test_structure.py`, estrutura de entrega e validade do `lab.json`.

O arquivo `conftest.py` coloca `src` no caminho de importação, então os testes
rodam sem instalação prévia do pacote.

## Estrutura do projeto

```text
Lab_tecnico_1_M2_processamento_de_imagens/
├── README.md
├── REPORT.md
├── AI_USAGE.md
├── lab.json
├── requirements.txt
├── pyproject.toml
├── conftest.py
├── lab_1_m2.py              reprodução de todas as saídas
├── laboratorio_1_M2.md      enunciado do laboratório
├── src/
│   └── pdi_lab/
│       ├── __init__.py
│       ├── __main__.py      permite python -m pdi_lab
│       ├── cli.py           argumentos, despacho e códigos de saída
│       ├── errors.py        erro de domínio
│       ├── image_io.py      leitura e escrita, com guardas
│       └── segmentation.py  métodos, validação e sobreposição
├── tests/
├── images/
│   ├── input/               coins.png e moedas_real_separadas.jpg
│   └── output/              máscaras, sobreposições e figuras
└── results/                 tabelas e registro de execução
```

## Imagens de entrada

- `images/input/coins.png`, 384 x 303, em cinza. Vem do scikit-image v0.26.0
  e é uma foto de moedas gregas do acervo do Brooklyn Museum, sem restrições
  de copyright conhecidas. É a imagem com dificuldade real: o fundo tem tons
  de cinza parecidos com os das moedas.
- `images/input/moedas_real_separadas.jpg`, 3664 x 2748, colorida. Foto
  "Moedas do Real até 2010.jpg", de Anderson Batista Evangelista Lima
  (MisterSanderson), publicada no Wikimedia Commons em
  https://commons.wikimedia.org/wiki/File:Moedas_do_Real_at%C3%A9_2010.jpg,
  sob a licença Creative Commons Atribuição-CompartilhaIgual 2.5 Genérica
  (CC BY-SA 2.5). O arquivo foi baixado sem alteração e só renomeado. É a
  imagem em condição favorável: 12 moedas separadas sobre fundo claro.

Como a foto está sob CC BY-SA 2.5, as máscaras, sobreposições e figuras
derivadas dela ficam sob a mesma licença.

## Convenções de nomes das saídas

| Arquivo | Conteúdo |
|---|---|
| `<imagem>_mask_<config>.png` | máscara de cada configuração: `fixed`, `otsu` e, na foto colorida, `hsv` |
| `<imagem>_overlay_<config>.png` | sobreposição de cada configuração, reduzida para 1280 pixels no lado maior porque é só visualização; a máscara fica no tamanho original |
| `<imagem>_mask.png` | máscara escolhida, entrada do M2.2 |
| `<imagem>_comparacao.png` | original, as máscaras de cada configuração e a sobreposição escolhida |
| `results/foreground.csv` | proporção de primeiro plano por imagem e configuração |
| `results/threshold_sensitivity.csv` | proporção de primeiro plano variando o limiar fixo de 5 em 5 |

A máscara é gravada exatamente no caminho de `--output`. Um diretório ou um
caminho sem extensão é recusado com erro.
