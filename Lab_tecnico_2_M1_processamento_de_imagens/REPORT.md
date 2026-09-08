# Relatório técnico M1.2

## 1. Identificação

- Estudante: Kauan Rocha Dalfovo
- Laboratório: M1.2, transformações de intensidade
- Disciplina: Processamento de Imagens, 2026-02
- Linguagem: Python 3.13.14, com numpy 2.5.2 e opencv-python 5.0.0.93

## 2. Objetivo

Implementar manualmente, com percurso explícito dos pixels, as transformações
pontuais de brilho, contraste, negativo e limiarização binária, além do cálculo
do histograma, e analisar como cada uma altera a distribuição das intensidades.

## 3. Operações implementadas

| Operação | Fórmula | Parâmetro | Saídas geradas |
|---|---|---|---|
| `brightness` | `g = f + b` | `--value` | `brightness_pos50.png`, `brightness_neg50.png` |
| `contrast` | `g = alpha (f - 128) + 128` | `--alpha` | `contrast_0_5.png`, `contrast_1_0.png`, `contrast_1_5.png` |
| `negative` | `g = 255 - f` | nenhum | `negative.png` |
| `threshold` | `g = 255 se f >= T, senão 0` | `--threshold` | `threshold_128.png`, `threshold_64.png` |
| `histogram` | contagem em 256 posições | nenhum | dez arquivos CSV em `results/` |
| `grayscale_weighted` | `g = 0,299R + 0,587G + 0,114B` | nenhum | `gray_weighted.png` |

Todas estão em `src/pdi_lab/operations.py`.

## 4. Decisões de implementação

### 4.1 O que já estava correto

A lógica das cinco transformações da versão anterior deste laboratório estava
correta. O ajuste de brilho já convertia para `int` antes de somar, o contraste
já acumulava em ponto flutuante, o negativo e a limiarização já produziam os
valores esperados, e o histograma já contava as 256 posições manualmente. O
problema de estouro em `uint8` que apareceu durante o desenvolvimento, relatado
em `mural.md`, já havia sido resolvido.

As mudanças desta versão são de formato, guardas, interface e organização, não
de algoritmo. O teste `test_brilho_nao_da_a_volta_no_uint8` fixa aquele
comportamento como regressão, para que a correção não se perca.

### 4.2 Formato do histograma

A versão anterior gravava arquivos `.txt` com nome contendo espaços, cabeçalho
`intensidade,quantidade` e separador com espaço depois da vírgula, no formato
`0, 171`. O contrato técnico define CSV com cabeçalho `intensity,count` e 256
linhas de dados. O formato foi corrigido, e o teste
`test_formato_csv_do_histograma` verifica cabeçalho, quantidade de linhas e
conteúdo.

### 4.3 Percurso único e transformação por pixel

As quatro transformações compartilham a função `_map_pixels`, que percorre a
imagem e aplica uma função a cada pixel. Cada operação fornece apenas a sua
fórmula. Isso evita repetir quatro vezes o mesmo laço e concentra em um único
lugar a conversão de linha, a saturação e o arredondamento.

O percurso converte cada linha para lista Python com `tolist()`. Isso mantém o
acesso pixel a pixel e faz as contas fora do `uint8`, onde `200 + 100` daria 44
em vez de 255.

### 4.4 Arredondamento determinístico

A função `round` do Python usa arredondamento bancário, no qual 0,5 vira 0 e
2,5 vira 2. Foi implementado `_round_half_up`, que sempre desempata para cima,
para que o resultado seja igual ao cálculo manual. Isso importa no contraste,
onde `alpha = 0,5` produz muitos resultados terminados em 0,5. Por exemplo,
`0,5 (255 - 128) + 128 = 191,5`, que vira 192.

### 4.5 Saturação apenas no momento da escrita

Os acumuladores trabalham em inteiro ou ponto flutuante sem limite. O corte
para 0 e 255 acontece somente em `_clamp_to_uint8`, na hora de gravar.

### 4.6 Critério da limiarização

O enunciado define `255` para `f >= T` e `0` para `f < T`. O pixel igual ao
limiar, portanto, vira 255. O teste
`test_limiarizacao_inclui_o_proprio_limiar` fixa esse critério, porque a
convenção oposta é comum e produziria uma imagem diferente.

### 4.7 Entrada colorida

As transformações atuam sobre imagens em níveis de cinza. Quando a entrada é
colorida, a conversão ponderada é aplicada antes, de forma explícita, para que
os mesmos comandos funcionem com qualquer imagem.

### 4.8 Guardas

| Situação | Comportamento |
|---|---|
| arquivo inexistente ou ilegível | erro explicativo, código de saída 1 |
| imagem que não é de 8 bits | recusada na leitura |
| imagem com 4 canais, BGRA | recusada na leitura |
| `--alpha` negativo, `nan` ou `inf` | erro explicativo |
| `--threshold` fora de 0 a 255 | erro explicativo |
| `--value` não inteiro | rejeitado pelo `argparse`, código 2 |
| parâmetro obrigatório ausente | erro explicativo |
| operação desconhecida | código de saída 2 |
| diretório de saída inexistente | criado automaticamente |
| valores fora de 0 a 255 | saturados na escrita |

A versão anterior não tratava `cv.imread` devolvendo `None`, o que derrubava o
programa com `AttributeError` em vez de mensagem clara.

## 5. Testes realizados

`python -m pytest` executa 60 testes, todos aprovados em 0,88 segundo.

Cobertura:

- valores conferidos à mão em imagem 2 por 2 com os pixels 0, 100, 200 e 255,
  para as quatro transformações;
- brilho positivo e negativo, incluindo o caso em que 255 mais 50 satura e o
  caso em que 0 menos 50 satura;
- contraste com 0,5, 1,0 e 1,5, mais os casos extremos `alpha = 0`, que achata
  tudo em 128, e a preservação do ponto fixo 128 em qualquer `alpha`;
- identidades matemáticas: `brightness` com 0 e `contrast` com 1,0 devolvem a
  imagem original, e o negativo aplicado duas vezes também;
- limiarização com dois limiares distintos, nos extremos 0 e 255, e verificação
  de que a saída contém apenas dois valores;
- histograma: soma igual ao total de pixels, imagem constante concentrada em um
  nível, imagem binária ocupando apenas duas posições;
- formato do CSV, com cabeçalho e 257 linhas;
- imagem de um único pixel e entrada colorida;
- todas as guardas listadas na seção anterior;
- códigos de saída 0, 1 e 2 pela linha de comando.

## 6. Resultados

Resumo estatístico calculado a partir dos histogramas, em `results/summary.csv`.
A entrada é `images/input/aura.png`, com 638 por 480, ou seja 306240 pixels.

| Imagem | Média | Desvio | Mín | Máx | Níveis usados | Pixels em 0 | Pixels em 255 |
|---|---:|---:|---:|---:|---:|---:|---:|
| original | 103,21 | 56,04 | 0 | 249 | 250 | 51 | 0 |
| brilho +50 | 153,09 | 55,79 | 50 | 255 | 206 | 0 | 5471 |
| brilho -50 | 58,32 | 49,10 | 0 | 199 | 200 | 63777 | 0 |
| contraste 0,5 | 115,86 | 28,02 | 64 | 189 | 126 | 0 | 0 |
| contraste 1,0 | 103,21 | 56,04 | 0 | 249 | 250 | 51 | 0 |
| contraste 1,5 | 96,48 | 76,16 | 0 | 255 | 172 | 55570 | 2004 |
| negativo | 151,79 | 56,04 | 6 | 255 | 250 | 0 | 51 |
| limiar 128 | 93,48 | 122,88 | 0 | 255 | 2 | 193980 | 112260 |
| limiar 64 | 187,95 | 112,26 | 0 | 255 | 2 | 80524 | 225716 |

Rampa sintética `images/input/ramp.png`, com 256 por 64 e exatamente 64 pixels
por intensidade:

| Imagem | Média | Desvio | Níveis usados | Pixels em 0 | Pixels em 255 |
|---|---:|---:|---:|---:|---:|
| rampa | 127,50 | 73,90 | 256 | 64 | 64 |
| rampa, brilho +50 | 172,52 | 67,06 | 206 | 0 | 3264 |
| rampa, contraste 1,5 | 127,50 | 95,18 | 172 | 2752 | 2752 |

Identidades verificadas diretamente sobre os arquivos CSV:

| Verificação | Resultado |
|---|---|
| soma do histograma igual ao total de pixels | 306240, correto |
| histograma do negativo é o espelho do original, posição a posição | sim |
| contagem em 255 após brilho +50, igual à soma das contagens originais de 205 a 255 | 5471 nos dois lados |
| contagem em 0 após limiar 128, igual à soma das contagens originais de 0 a 127 | 193980 nos dois lados |
| rampa com contagem uniforme | 64 em todas as 256 intensidades |
| contraste 1,0 idêntico à original em média, desvio, faixa e níveis | sim |

## 7. Análise técnica

### 7.1 Diferença entre alterar brilho e alterar contraste

Brilho soma uma constante a todos os pixels. A distribuição inteira se desloca
sem mudar de forma, portanto a média muda e o desvio padrão fica praticamente
igual: 56,04 na original contra 55,79 após somar 50.

Contraste multiplica a distância de cada pixel até o ponto fixo 128. A forma
muda: o desvio padrão escala junto com `alpha`. Com `alpha = 0,5` o desvio caiu
de 56,04 para 28,02, exatamente metade, a menos do arredondamento.

Há um efeito do contraste que não é óbvio. Com `alpha = 0,5` a média subiu de
103,21 para 115,86, mesmo o contraste sendo uma operação centrada. Isso
acontece porque a imagem tem média abaixo de 128, e comprimir em direção a 128
puxa a média para cima. Se a distribuição estivesse centrada em 128, como na
rampa, a média não mudaria, e é o que se observa: a rampa mantém 127,50 depois
do contraste 1,5.

### 7.2 Onde ocorreu saturação e qual foi o efeito

Saturação ocorreu em quatro dos testes:

| Teste | Pixels saturados |
|---|---|
| brilho +50 | 5471 em 255 |
| brilho -50 | 63777 em 0 |
| contraste 1,5 | 55570 em 0 e 2004 em 255 |
| rampa, brilho +50 | 3264 em 255 |

O efeito é perda irreversível de informação, e aparece de três formas nos
dados.

Primeiro, redução do número de níveis usados. A original ocupa 250 níveis; após
brilho +50 sobram 206, porque 51 intensidades diferentes colapsaram no mesmo
valor 255. Na rampa isso é exato e conferível: as intensidades de 205 a 255 são
51 valores, cada um com 64 pixels, e 51 vezes 64 é 3264, exatamente a contagem
observada em 255.

Segundo, deslocamento menor que o esperado. Somar 50 deveria levar a média de
103,21 para 153,21, e ela ficou em 153,09. Somar -50 deveria levar a 53,21, e
ficou em 58,32. A diferença é grande no caso negativo porque 63777 pixels
travaram em 0 e pararam de descer.

Terceiro, ganho de contraste menor que o pedido. Com `alpha = 1,5` o desvio
deveria ir para 84,06, que é 1,5 vezes 56,04, e ficou em 76,16. A saturação
comprime as caudas justamente onde o espalhamento seria maior.

Na rampa esse último efeito pode ser conferido à mão. Com `alpha = 1,5`, satura
por cima quando `1,5 (v - 128) + 128` passa de 255, ou seja a partir de
`v = 213`, o que dá 43 intensidades, e por baixo de forma simétrica, `v` até
42, outras 43. Como cada intensidade tem 64 pixels, o esperado é 43 vezes 64,
igual a 2752 em cada extremo, que é exatamente o valor observado.

### 7.3 Como o histograma se deslocou após alterar o brilho

O histograma se desloca em bloco, na mesma quantidade somada, e acumula no
extremo o que ultrapassa o limite.

A verificação direta é esta: a contagem na posição 255 do histograma após
brilho +50 é 5471, e a soma das contagens do histograma original das posições
205 até 255 também é 5471. Ou seja, todas as intensidades que passariam de 255
foram empilhadas na última posição.

A faixa ocupada acompanha: a original vai de 0 a 249, e após somar 50 vai de 50
a 255. O mínimo subiu exatamente 50, o máximo travou no limite.

Na rampa, cujo histograma é uma linha reta com 64 em cada posição, o resultado
é uma reta idêntica deslocada 50 posições à direita, com uma barra alta de 3264
em 255.

### 7.4 Como a distribuição mudou ao alterar o contraste

Depende do lado de 1 em que `alpha` está, e as duas direções perdem níveis por
motivos diferentes.

Com `alpha = 0,5` a distribuição comprime em torno de 128. A faixa passou de
`[0, 249]` para `[64, 189]`, e os níveis usados caíram de 250 para 126. A perda
aqui é por colisão: intensidades vizinhas passam a produzir o mesmo valor de
saída, porque a faixa de destino é menor que a de origem. Nenhum pixel saturou,
e ainda assim informação foi perdida. Os 126 níveis correspondem exatamente ao
tamanho do intervalo de 64 a 189, ou seja todos os valores possíveis do destino
foram atingidos.

Com `alpha = 1,5` a distribuição se afasta de 128. Os níveis usados caíram de
250 para 172, mas por dois motivos somados: saturação nos extremos, 55570
pixels em 0 e 2004 em 255, e lacunas no meio, porque a multiplicação por 1,5
faz o resultado pular valores que nenhum pixel de entrada consegue produzir.

Na rampa dá para separar os dois efeitos. Das 256 intensidades, 43 saturam em
cada extremo, sobrando 170 que são mapeadas para 170 valores distintos. Somando
os dois níveis saturados, 0 e 255, chega-se a 172, exatamente o observado.

Uma observação que vale registrar: aumentar o contraste não aumenta a
quantidade de informação. Ele redistribui a informação existente e ainda
descarta parte dela.

### 7.5 Que informação é perdida após a limiarização

Perde-se tudo, exceto a relação de ordem de cada pixel em relação ao limiar. A
imagem sai com 2 níveis, contra os 250 da original, e a operação não é
inversível.

Com limiar 128, os 193980 pixels que viraram 0 correspondem exatamente à soma
das contagens originais de 0 até 127. Depois disso, não há como saber se um
pixel preto valia 3 ou 127. Textura, sombreado e qualquer gradiente interno
desaparecem, e resta a silhueta.

A escolha do limiar decide o que sobra. Com 128, a divisão fica em 193980
contra 112260 pixels. Com 64, ela fica em 80524 contra 225716. É o mesmo
conteúdo original, particionado de duas formas bem diferentes, e nenhuma das
duas guarda informação suficiente para reconstruir a outra.

## 8. Limitações

- As transformações são pontuais, portanto ignoram qualquer relação de
  vizinhança. Ruído isolado não é atenuado, e um pixel errado permanece errado.
  Operações de vizinhança são o objeto do M1.3.
- A saturação é irreversível. Uma vez que 5471 pixels chegaram a 255, aplicar
  brilho -50 não recupera os valores originais.
- O limiar é global e fixo. Em imagens com iluminação desigual, nenhum valor
  único separa bem a cena inteira. Métodos adaptativos ou automáticos, como
  Otsu, não fazem parte do escopo.
- As atividades complementares do enunciado, que são opcionais, não foram
  implementadas: seleção por intervalo, expansão linear de contraste e
  transformação gama.
- O percurso explícito, sem vetorização, custa cerca de 1,3 segundo nesta
  imagem de 306 mil pixels. Em imagens muito maiores o custo cresce
  proporcionalmente. A restrição vem do enunciado, que exige implementação
  manual.
- O diretório `kernels/` está vazio. Ele faz parte da estrutura comum da
  disciplina e passa a ser usado a partir do M1.3.

## 9. Declaração de uso de IA

Houve uso de IA generativa. Os detalhes estão em [AI_USAGE.md](AI_USAGE.md).

## 10. Referências

- Enunciado do laboratório: [laboratorio_M1_2.md](laboratorio_M1_2.md)
- Relato da evidência parcial: [mural.md](mural.md)
- Contrato técnico dos laboratórios da M1: `lab_tecnico.md`, na raiz do
  repositório
- Rubrica geral: `rubrica_avaliativa.md`, na raiz do repositório
- Documentação do OpenCV sobre leitura e escrita de imagens, módulo `imgcodecs`
- Documentação do NumPy sobre regras de promoção de tipo, NEP 50
