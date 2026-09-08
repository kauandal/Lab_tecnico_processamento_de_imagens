# Relatório técnico M1.1

## 1. Identificação

- Estudante: Kauan Rocha Dalfovo
- Laboratório: M1.1, representação, canais e níveis de cinza
- Disciplina: Processamento de Imagens, 2026-02
- Linguagem: Python 3.13.14, com numpy 2.5.2 e opencv-python 5.0.0.93

## 2. Objetivo

Implementar manualmente, com percurso explícito dos pixels, as operações de
inspeção, cópia, separação de canais, conversão para níveis de cinza pelas duas
fórmulas e quantização, analisando o efeito da redução de resolução
radiométrica.

## 3. Operações implementadas

| Operação | Função | Saída gerada |
|---|---|---|
| `inspect` | `inspect_image` | `results/inspect.txt` |
| `copy` | `copy_image` | `images/output/copy.png` |
| `channel_b`, `channel_g`, `channel_r` | `extract_channel` | `images/output/channel_*.png` |
| `grayscale_average` | `grayscale_average` | `images/output/gray_average.png` |
| `grayscale_weighted` | `grayscale_weighted` | `images/output/gray_weighted.png` |
| `quantize` | `quantize` | `images/output/quant_16.png`, `quant_8.png`, `quant_4.png`, `quant_2.png` |

Todas estão em `src/pdi_lab/operations.py`. A biblioteca é usada só para abrir
e salvar arquivos e para alocar matrizes.

## 4. Decisões de implementação

### 4.1 Correção de estouro na média simples

A primeira versão calculava a média simples somando os três canais direto dos
valores `uint8`:

```python
simples[i][j] = (img[i][j][0] + img[i][j][1] + img[i][j][2]) / 3
```

No NumPy 2.x a soma de três `uint8` permanece `uint8` e dá a volta em 255. Um
pixel branco, `(255, 255, 255)`, somava 253 em vez de 765, e o resultado virava
84 em vez de 255. A imagem inteira saía com aproximadamente um terço da
intensidade correta: o máximo do arquivo `gray_average.png` era 85.

A correção converte cada linha para lista Python com `tolist()` antes do
percurso. Os valores passam a ser inteiros de precisão arbitrária do Python,
que não estouram. A média ponderada nunca sofreu o problema porque a
multiplicação pelos pesos já promove os valores a ponto flutuante.

O teste `test_media_simples_nao_estoura_em_pixel_branco` fixa esse
comportamento como regressão.

### 4.2 Percurso dos pixels por linha

O percurso é explícito, pixel a pixel, mas a linha é convertida para lista
antes do laço interno. Isso mantém o algoritmo manual, evita o custo de indexar
o NumPy elemento a elemento e resolve o problema de tipo descrito acima. A
conversão acontece uma linha por vez, o que mantém o uso de memória baixo mesmo
na imagem de 32 megapixels.

### 4.3 Arredondamento determinístico

A função `round` do Python usa arredondamento bancário, no qual 0,5 vira 0 e
2,5 vira 2. Como o enunciado pede resultado conferível à mão, foi implementado
`_round_half_up`, que sempre desempata para cima. Isso garante o mesmo valor em
qualquer execução e igual ao cálculo manual.

### 4.4 Saturação apenas no momento da escrita

Os acumuladores trabalham em inteiro ou ponto flutuante sem limite. O corte
para o intervalo de 0 a 255 acontece somente em `_clamp_to_uint8`, na hora de
gravar o valor no resultado.

### 4.5 Contagem de pixels

`inspect` reporta `pixels` como largura vezes altura, sem multiplicar pelo
número de canais. A versão anterior usava `img.size`, que devolvia 3 vezes o
valor correto em imagens coloridas. O exemplo do contrato técnico confirma o
critério: 640 por 480 com 3 canais resulta em 307200 pixels.

### 4.6 Quantização a partir de imagem colorida

O enunciado parte de uma imagem em níveis de cinza. Quando `quantize` recebe
uma imagem colorida, a conversão ponderada é aplicada antes, de forma explícita
e documentada, para que o mesmo comando funcione com qualquer entrada.

O passo é `255 / (levels - 1)`, o que faz o menor nível ser 0 e o maior ser 255
em qualquer quantidade de níveis. O índice é limitado ao intervalo de 0 até
`levels - 1` antes de voltar para a escala de cinza.

### 4.7 Guardas

| Situação | Comportamento |
|---|---|
| arquivo inexistente ou ilegível | erro explicativo, código de saída 1 |
| imagem que não é de 8 bits | recusada na leitura |
| imagem com 4 canais, BGRA | recusada na leitura |
| operação de cor em imagem de 1 canal | erro explicativo |
| canal diferente de b, g ou r | erro explicativo |
| `--levels` fora do intervalo de 2 a 256, ou não inteiro | erro explicativo |
| `quantize` sem `--levels` | erro explicativo |
| operação de imagem sem `--output` | erro explicativo |
| operação desconhecida | código de saída 2, tratado pelo `argparse` |
| diretório de saída inexistente | criado automaticamente |
| valores fora de 0 a 255 | saturados na escrita |

## 5. Testes realizados

`python -m pytest` executa 44 testes, todos aprovados em 0,15 segundo.

Cobertura por tipo:

- valores conferíveis à mão, em imagem sintética 2 por 2 que contém preto,
  branco e dois tons médios;
- cópia numericamente idêntica, em imagem colorida e em níveis de cinza;
- ordem dos canais na convenção BGR do OpenCV, verificando que a soma dos três
  canais isolados reconstrói a imagem original;
- as duas fórmulas de cinza, com o valor esperado calculado no comentário do
  teste;
- regressão do estouro em pixel branco;
- contagem exata de níveis após a quantização, com rampa de 0 a 255;
- preservação dos extremos 0 e 255 em todas as quantidades de níveis;
- imagem de um único pixel e imagem constante;
- todas as guardas listadas na seção anterior;
- códigos de saída 0, 1 e 2 pela linha de comando.

## 6. Resultados

Inspeção de `images/input/aura_small.png`:

```text
width=638
height=480
channels=3
pixels=306240
type=uint8
min=0
max=255
mean=102.8340
min_b=0    max_b=255    mean_b=72.4239
min_g=0    max_g=255    mean_g=84.6324
min_r=0    max_r=255    mean_r=151.4457
```

Verificações sobre as saídas geradas:

| Verificação | Resultado |
|---|---|
| `copy.png` idêntica à entrada, pixel a pixel | sim |
| soma de `channel_b` + `channel_g` + `channel_r` igual à original | sim |
| `gray_average.png` e `gray_weighted.png` com 1 canal | sim |
| `gray_average.png`, faixa de valores | 0 a 245, 246 níveis distintos |
| `gray_weighted.png`, faixa de valores | 0 a 249, 250 níveis distintos |
| `quant_16`, `quant_8`, `quant_4`, `quant_2`, níveis distintos | 16, 8, 4 e 2 |
| extremos 0 e 255 preservados nas quantizações | sim |

Comparação entre as duas conversões para cinza:

| Métrica | Valor |
|---|---|
| diferença média por pixel | 24,18 |
| diferença máxima por pixel | 55 |
| pixels com valores diferentes | 99,0% |
| média global, simples | 102,83 |
| média global, ponderada | 103,21 |

Erro da quantização em relação a `gray_weighted.png`:

| Níveis | Passo | Erro médio | Erro máximo |
|---:|---:|---:|---:|
| 16 | 17,00 | 4,24 | 8 |
| 8 | 36,43 | 9,19 | 18 |
| 4 | 85,00 | 20,00 | 42 |
| 2 | 255,00 | 76,15 | 127 |

## 7. Análise técnica

### 7.1 Diferença entre resolução espacial e resolução radiométrica

Resolução espacial é a quantidade de amostras usadas para representar a cena,
ou seja, largura por altura. Ela define o menor detalhe geométrico que pode
aparecer. Na imagem usada, 638 por 480, são 306240 amostras.

Resolução radiométrica é a quantidade de valores distintos que cada amostra
pode assumir, definida pela profundidade de bits. Com 8 bits são 256 valores
por canal. Ela define o menor degrau de intensidade que pode ser distinguido.

As duas são independentes. A quantização deste laboratório reduz apenas a
segunda: as imagens `quant_*` continuam com 638 por 480 amostras, mas com 16, 8,
4 ou 2 valores possíveis.

### 7.2 Por que a média ponderada difere da média simples

A média simples trata os três canais como igualmente importantes. A ponderada
usa os coeficientes de luminância, 0,299 para o vermelho, 0,587 para o verde e
0,114 para o azul, que aproximam a sensibilidade do olho humano, mais alta no
verde e mais baixa no azul.

A diferença entre as duas depende de quanto os canais divergem entre si. Nesta
imagem, a média do canal vermelho é 151,45 e a do azul é 72,42, uma diferença
grande. O resultado é que 99% dos pixels ficaram diferentes, com diferença média
de 24 níveis e máxima de 55.

Um detalhe que chama atenção: as médias globais ficaram quase iguais, 102,83
contra 103,21. Isso é coincidência desta imagem, em que o peso maior dado ao
verde compensa o peso menor dado ao vermelho no agregado. A coincidência não se
repete pixel a pixel, como mostra a diferença máxima de 55. Comparar médias
globais, portanto, não serve para avaliar se duas conversões são equivalentes.

### 7.3 Efeito visual da redução de níveis

Cada redução divide o número de valores disponíveis, o que aumenta o passo
entre níveis consecutivos. Transições que eram contínuas passam a ser degraus,
efeito conhecido como banda, ou contorno falso.

O erro médio confirma a progressão: 4,24 com 16 níveis, 9,19 com 8, 20,00 com 4
e 76,15 com 2. Com 16 níveis o efeito ainda é discreto, porque o passo de 17 é
próximo do limite de percepção em áreas texturizadas. Com 4 níveis os degraus
ficam evidentes. Com 2 níveis a operação degenera em uma limiarização em 128,
e resta apenas a silhueta.

### 7.4 Onde a perda de informação é mais evidente

A perda é mais visível em regiões de variação suave, como fundos, céus e
sombreados, porque nelas o gradiente original é menor que o passo de
quantização. O resultado é um degrau contínuo e alinhado, que o olho identifica
como contorno artificial.

Vale registrar uma medição que contraria a intuição: o erro numérico não é
maior nessas regiões. Separando a imagem entre área suave, com gradiente local
abaixo de 2, e área de borda, o erro médio da quantização em 8 níveis foi 9,32
na área suave e 9,17 na área de borda, praticamente igual. A área suave
representa apenas 11,4% desta imagem.

A conclusão é que o problema não é a magnitude do erro, e sim a sua correlação
espacial. Em área texturizada o erro varia de pixel para pixel e é mascarado
pelo próprio detalhe. Em área suave o erro é o mesmo para vizinhos inteiros,
formando faixas visíveis. Uma métrica puramente numérica não captura essa
diferença.

### 7.5 Como tipo e número de canais interferem no acesso ao pixel

O número de canais muda a forma do arranjo. Uma imagem em níveis de cinza tem
duas dimensões, e `image[y][x]` devolve um escalar. Uma imagem colorida tem três
dimensões, e `image[y][x]` devolve uma sequência de três valores, na ordem BGR
no OpenCV, e não RGB. Escrever a fórmula da luminância assumindo a ordem RGB
inverte os pesos do azul e do vermelho.

O tipo determina o comportamento aritmético. Com `uint8`, qualquer soma
intermediária acima de 255 dá a volta em silêncio, que foi exatamente a causa
do defeito descrito na seção 4.1. Por isso o código faz as contas fora do
`uint8` e converte de volta apenas na escrita.

O código trata as duas situações explicitamente: `channel_count` identifica o
formato, `require_color` recusa entradas incompatíveis com mensagem clara, e as
saídas em níveis de cinza são gravadas com um único canal.

## 8. Limitações

- O percurso explícito, sem vetorização, custa cerca de 9 minutos para gerar o
  conjunto completo a partir da imagem de 32 megapixels, contra 1 segundo na
  versão de 638 por 480. As saídas versionadas usam a versão menor. A restrição
  vem do enunciado, que exige implementação manual, e não de limitação do
  algoritmo.
- Apenas imagens de 8 bits são aceitas. Entradas de 16 bits ou com canal alfa
  são recusadas na leitura, com mensagem, em vez de convertidas.
- A quantização distribui os níveis uniformemente. Métodos adaptativos, que
  posicionam os níveis conforme o histograma, não fazem parte do escopo do
  laboratório.
- A análise da seção 7.4 usa um limiar de gradiente arbitrário para separar
  área suave de área de borda. O valor 2 foi escolhido por inspeção, não por
  critério formal.
- O diretório `kernels/` está vazio. Ele faz parte da estrutura comum da
  disciplina e passa a ser usado a partir do M1.3.

## 9. Declaração de uso de IA

Houve uso de IA generativa. Os detalhes estão em [AI_USAGE.md](AI_USAGE.md).

## 10. Referências

- Enunciado do laboratório: [lab_1_m1.md](lab_1_m1.md)
- Contrato técnico dos laboratórios da M1: `lab_tecnico.md`, na raiz do
  repositório
- Rubrica geral: `rubrica_avaliativa.md`, na raiz do repositório
- Documentação do OpenCV sobre leitura e escrita de imagens, módulo `imgcodecs`
- Documentação do NumPy sobre regras de promoção de tipo, NEP 50, que explica a
  permanência em `uint8` na soma descrita na seção 4.1
