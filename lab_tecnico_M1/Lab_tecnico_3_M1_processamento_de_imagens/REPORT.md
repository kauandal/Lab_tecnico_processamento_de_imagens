# Relatório técnico M1.3

## 1. Identificação

- Estudante: Kauan Rocha Dalfovo
- Laboratório: M1.3, convolução e filtragem espacial
- Disciplina: Processamento de Imagens, 2026-02
- Linguagem: Python 3.13.14, com numpy 2.5.2 e opencv-python 5.0.0.93

## 2. Objetivo

Implementar operações de vizinhança no domínio espacial com percurso explícito,
tratando kernels, estratégias de borda, tipos numéricos e o momento correto da
saturação, e analisar o comportamento de suavização, Laplaciano e Sobel.

## 3. Operações implementadas

| Operação | Kernel ou fórmula | Saídas geradas |
|---|---|---|
| `convolution` | kernel lido de arquivo | `identity_replicate.png` |
| `mean_filter` | janela N por N, peso `1/N²` | `mean_3x3_replicate.png`, `mean_3x3_copy.png`, `mean_5x5_replicate.png` |
| `weighted_mean` | `[1 2 1; 2 4 2; 1 2 1] / 16` | `weighted_mean_3x3_replicate.png` |
| `laplacian` | `[0 1 0; 1 -4 1; 0 1 0]` | `laplacian_offset`, `laplacian_abs`, `laplacian_normalize` |
| `laplacian_enhance` | `g = f - λL` | `laplacian_enhance_replicate.png` |
| `sobel` | `Kx` e `Ky` do material | `sobel_gx`, `sobel_gy`, `sobel_l1`, `sobel_l2`, mais versões normalizadas |
| `grayscale_weighted` | luminância ponderada | `gray_weighted.png` |

Ao todo, 25 imagens em `images/output/` e 9 arquivos de evidência numérica em
`results/`.

## 4. Decisões de implementação

### 4.1 Convenção do kernel

Os coeficientes são aplicados na orientação em que estão escritos, sem giro de
180 graus, que é a convenção didática do material da disciplina.
Rigorosamente, a operação é uma correlação. Para média e gaussiano, simétricos,
as duas convenções coincidem. Para Sobel, o giro inverteria o sinal, mas não a
magnitude.

O teste `test_impulso_reproduz_a_forma_do_kernel` fixa a convenção: aplicando um
kernel assimétrico `[1 2 3; 4 5 6; 7 8 9]` sobre um impulso, o pixel acima e à
esquerda recebe o coeficiente 9, e não o 1. Se a implementação passasse a
espelhar o kernel, esse teste falharia.

### 4.2 Estrutura do percurso

Existe uma única função de vizinhança, `convolve`, e todas as demais operações
a utilizam. Média, média ponderada, Laplaciano e as duas componentes do Sobel
diferem apenas no kernel. Isso evita repetir o laço quádruplo e concentra o
tratamento de borda em um lugar só.

A limitação de coordenada é aplicada sempre, com `min` e `max`. No interior da
imagem ela não altera nada; na periferia, realiza a replicação. Isso mantém o
laço uniforme, sem um caminho separado para a borda.

### 4.3 Tipos numéricos e momento da saturação

O acumulador é `float` e a resposta bruta é devolvida em `float64`. Nada é
arredondado nem saturado durante o cálculo. A conversão para 8 bits acontece
apenas em `to_uint8`, no fim.

Isso é decisivo no Laplaciano: 47,0% dos pixels da resposta ficam fora da faixa
de 8 bits, e 143851 deles são negativos. Saturar antes descartaria quase metade
da informação e tornaria o realce incorreto.

### 4.4 Realce

O realce usa `g = f - λL` com o kernel de centro `-4`. A subtração corresponde
a esse sinal: onde o centro é mais claro que a vizinhança a resposta é
negativa, e subtrair torna o centro ainda mais claro.

O teste `test_realce_equivale_ao_kernel_de_afiamento` confirma numericamente
que, com `λ = 1`, o resultado é idêntico ao da convolução direta com
`[0 -1 0; -1 5 -1; 0 -1 0]`.

### 4.5 Visualização declarada

As respostas derivativas não cabem em 8 bits, então a imagem exibida não contém
mais os valores brutos. O programa oferece quatro modos, `clamp`, `abs`,
`offset` e `normalize`, imprime na saída padrão qual foi usado, e registra o
modo no nome do arquivo. O parâmetro `--raw-output` grava a resposta antes de
qualquer conversão.

Para o Laplaciano foram gravadas as três visualizações da mesma resposta bruta,
para que a diferença entre elas fique explícita.

### 4.6 Tolerância em ponto flutuante

Somar nove parcelas de `255/9` em ponto flutuante devolve 255,00000000000003.
Sem tolerância, o resumo estatístico contaria esses pixels como valores fora da
faixa de 8 bits, o que não descreve o comportamento do filtro. As comparações
de `response_summary` usam tolerância de 1e-9.

### 4.7 Kernels de arquivo não são normalizados

Os arquivos `mean_3x3.txt` e `mean_5x5.txt` trazem coeficientes iguais a 1, como
fornecidos pela disciplina. A operação `convolution` aplica o kernel exatamente
como está, então usá-lo direto produz uma resposta nove vezes maior que a
média, e não a média. A normalização acontece em `mean_filter` e em
`weighted_mean`. A alternativa é informar `--scale`. Essa separação evita o erro
de dividir duas vezes, apontado no material.

Kernels cuja soma dos coeficientes é zero, como Laplaciano e Sobel, não são
normalizados pela função `normalized`, que os devolve intactos.

### 4.8 Guardas

| Situação | Comportamento |
|---|---|
| arquivo de imagem inexistente ou ilegível | erro explicativo, código 1 |
| imagem que não é de 8 bits, ou com canal alfa | recusada na leitura |
| `--kernel` ausente em `convolution` | erro explicativo |
| arquivo de kernel inexistente ou vazio | erro explicativo |
| cabeçalho do kernel ausente, incompleto ou não numérico | erro explicativo |
| quantidade de valores diferente do cabeçalho | erro explicativo |
| kernel não quadrado | erro explicativo |
| kernel de dimensão par | erro explicativo |
| kernel com valor não numérico | erro explicativo |
| `--size` par, zero ou negativo | erro explicativo |
| `--border` fora de `copy` e `replicate` | código 2 |
| `--view` inválido | código 2 |
| fator de realce não finito | erro explicativo |
| acesso fora dos limites | impossível: toda coordenada passa pela limitação |
| valores negativos ou acima de 255 | preservados na resposta bruta, saturados só na visualização |

## 5. Testes realizados

`python -m pytest` executa 92 testes, todos aprovados em 0,20 segundo.

Casos mínimos exigidos pelo enunciado e onde estão cobertos:

| Caso | Verificação |
|---|---|
| kernel identidade | reproduz a imagem, nas duas estratégias de borda |
| imagem constante | média preserva o valor; Laplaciano e Sobel respondem zero |
| impulso | média espalha `255/9` em nove posições; a resposta reproduz a forma do kernel |
| degrau vertical | `Gx` chega a 1020 e `Gy` é identicamente zero |
| degrau horizontal | `Gy` chega a 1020 e `Gx` é identicamente zero |
| formas geométricas | quadrado isolado, barra e faixa |
| conteúdo tocando as bordas | barra encostada na moldura, usada na comparação de bordas |
| kernel 3 por 3 | toda a suíte |
| kernel 5 por 5 | média 5 por 5 e faixa de borda de raio 2 |

Além desses, os testes cobrem os valores numéricos do material: vizinhos 100 com
centro 150 dão `-200`, com centro 50 dão `+200`, e a vizinhança
`[[0,0,255],[0,0,255],[0,0,255]]` dá `Gx = 1020`. Também verificam a inversão de
sinal ao inverter a transição, a borda diagonal ativando as duas componentes, a
relação `L1 >= L2`, os quatro modos de visualização e todas as guardas.

## 6. Resultados

### 6.1 Resumo das respostas brutas

Extraído de `results/summary.csv`, para `images/input/aura.png`, com 306240
pixels e borda `replicate`.

| Resposta | Mín | Máx | Média | Negativos | Fora de 8 bits |
|---|---:|---:|---:|---:|---:|
| identidade | 0,00 | 249,00 | 103,2137 | 0 | 0 |
| média 3 por 3 | 0,67 | 246,44 | 103,2137 | 0 | 0 |
| média ponderada 3 por 3 | 0,50 | 246,88 | 103,2137 | 0 | 0 |
| média 5 por 5 | 1,24 | 240,64 | 103,2124 | 0 | 0 |
| Laplaciano | -415,00 | 345,00 | 0,0000 | 143851 | 143879 |
| Sobel `Gx` | -782,00 | 739,00 | -0,1260 | 149128 | 152789 |
| Sobel `Gy` | -934,00 | 833,00 | -0,7882 | 153172 | 157465 |
| Sobel `L1` | 0,00 | 1230,00 | 106,2265 | 0 | 29204 |
| Sobel `L2` | 0,00 | 934,26 | 83,9817 | 0 | 18339 |

A identidade reproduz a entrada e os três filtros de suavização preservam a
média global, como esperado de kernels cuja soma dos coeficientes é 1. O
Laplaciano tem média exatamente zero, o que é consequência direta de a soma dos
seus coeficientes ser zero.

### 6.2 Suavização

| Filtro | Desvio padrão global | Variação local média | Máximo |
|---|---:|---:|---:|
| original | 56,039 | 9,067 | 249 |
| média 3 por 3 | 54,067 | 5,560 | 246,44 |
| média ponderada 3 por 3 | 54,407 | 5,975 | 246,88 |
| média 5 por 5 | 52,510 | 4,183 | 240,64 |

A variação local média é a média de `|f(x+1,y) - f(x,y)|` sobre a imagem, e mede
diretamente quanto o filtro reduz as diferenças entre vizinhos.

### 6.3 Casos sintéticos

| Caso | Resultado |
|---|---|
| impulso com média 3 por 3 | nove posições com 28,3333, igual a `255/9`, e zero fora delas |
| degrau vertical, `Gx` | máximo 1020, com 32 posições ativas |
| degrau vertical, `Gy` | identicamente zero em toda a imagem |
| degrau horizontal, `Gy` | máximo 1020 |
| degrau horizontal, `Gx` | identicamente zero em toda a imagem |
| degrau vertical, Laplaciano | de -255 a +255, com 16 posições negativas e 16 positivas |

Os valores brutos estão em `results/raw_impulse_mean_3x3.csv`,
`results/raw_step_vertical_gx.csv` e nos demais arquivos `raw_`.

### 6.4 Comparação das estratégias de borda

Diferença absoluta entre `copy` e `replicate` na imagem `shapes.png`, por
distância até a borda, de `results/border_profile_mean_3.csv` e
`border_profile_mean_5.csv`.

| Distância da borda | Média 3 por 3, raio 1 | Média 5 por 5, raio 2 |
|---:|---:|---:|
| 0 | 5,6667 | 27,6100 |
| 1 | 0,0000 | 47,2385 |
| 2 | 0,0000 | 0,0000 |
| 3 | 0,0000 | 0,0000 |

A diferença é exatamente zero a partir da distância igual ao raio do kernel. Se
a imagem inteira mudasse ao trocar a estratégia, haveria erro de índices.

## 7. Análise técnica

### 7.1 Diferença entre operação pontual e operação de vizinhança

Numa operação pontual, como as do M1.2, o valor de saída depende só do pixel
correspondente da entrada. Numa operação de vizinhança, ele depende de uma
região, neste laboratório de 9 ou 25 pixels.

Três consequências práticas aparecem nos dados.

Primeira, surge o problema de borda. Um pixel na moldura não tem vizinhança
completa, o que não acontecia no M1.2. Foi preciso definir explicitamente o que
fazer, e a escolha muda o resultado, como mostra a seção 6.4.

Segunda, o resultado deixa de ser reversível pixel a pixel. Um negativo pode ser
desfeito aplicando o negativo de novo, mas não existe um valor de saída da média
que permita recuperar os nove valores de entrada.

Terceira, o custo passa a depender do tamanho do kernel, não apenas do número de
pixels.

### 7.2 Por que kernels normalmente possuem dimensões ímpares

Porque uma dimensão ímpar tem um elemento central, e é ele que se alinha ao
pixel de saída. Com lado `k` ímpar, o raio é `k // 2` e a vizinhança vai de
`-raio` a `+raio` de forma simétrica nas duas direções.

Com lado par não existe centro. A âncora cairia entre pixels, e o resultado
ficaria deslocado meio pixel, o que introduziria um desalinhamento sistemático
entre entrada e saída. Por isso a validação recusa kernels pares, junto com
kernels vazios e não quadrados.

### 7.3 Efeito de aumentar o tamanho do kernel de média

Aumentar a janela combina mais amostras, o que reduz mais a variação local e
apaga mais detalhes, com custo maior.

A variação local média cai de 9,067 na original para 5,560 com 3 por 3, uma
redução de 39%, e para 4,183 com 5 por 5, uma redução de 54%. O máximo da imagem
cai de 249 para 246,44 e depois para 240,64, ou seja o filtro maior consegue
puxar para baixo até os picos mais isolados.

O custo mereceu atenção. A média 5 por 5 faz 25 multiplicações por pixel contra
9, uma razão de 2,78. O tempo medido foi 0,62 segundo contra 0,29, razão de
2,13. A diferença aparece porque parte do trabalho por pixel é fixa, como o
cálculo dos índices e a escrita do resultado, e não escala com o tamanho do
kernel. O custo cresce com a área da janela, mas não exatamente na proporção
dela.

A comparação com a média ponderada mostra que o tamanho não é o único fator. Com
a mesma janela 3 por 3, a ponderada reduz a variação local para 5,975 contra
5,560 da média simples, ou seja suaviza menos, e preserva um máximo maior,
246,88 contra 246,44. O motivo é o peso central 4/16 contra 1/9: dar mais peso
ao centro preserva melhor o valor original do pixel. Na resposta ao impulso isso
fica explícito, 63,75 no centro contra 28,33.

### 7.4 Como a estratégia de bordas interfere no resultado

As duas estratégias produzem resultados idênticos no interior e divergem numa
faixa cuja largura é exatamente o raio do kernel. Com 3 por 3, a diferença
existe só na distância 0 e é zero a partir da distância 1. Com 5 por 5, existe
nas distâncias 0 e 1 e é zero a partir da 2.

A natureza da diferença é distinta em cada uma.

Com `copy`, a moldura não é filtrada, permanece com o valor original. A
consequência é uma descontinuidade de comportamento: o interior está suavizado e
a periferia não. Isso é visível no resumo, em que `shapes_mean_5` com `copy`
mantém máximo 255, que é o valor original preservado na moldura, enquanto com
`replicate` o máximo cai para 204, porque todo pixel foi efetivamente filtrado.

Com `replicate`, todos os pixels recebem o filtro, mas a vizinhança usada é
parcialmente inventada: o pixel da borda é repetido para fora do domínio. Isso
dá mais peso a esse pixel do que ele teria se houvesse dados reais. No teste com
uma barra clara encostada na borda esquerda, o pixel da coluna 0 recebe
`255 × 6/9`, porque a replicação faz a própria barra ocupar dois terços da
vizinhança.

Nenhuma das duas é neutra. `copy` preserva o dado original ao preço de não
filtrar, e `replicate` filtra tudo ao preço de extrapolar. A escolha precisa ser
declarada, porque muda o resultado numa região que costuma ser justamente onde
está o contorno do objeto.

### 7.5 Por que a resposta bruta do Laplaciano pode conter valores negativos

Porque a soma dos coeficientes do kernel é zero, o que faz a resposta ser uma
diferença, não uma média. Reescrevendo o cálculo:

```text
L = 4 * ( (média dos quatro vizinhos) - centro )
```

Quando o centro é mais claro que a vizinhança, a diferença é negativa. Com o
kernel de centro `-4` usado aqui, o teste do material confirma: vizinhos 100 com
centro 150 dão `-200`, e com centro 50 dão `+200`.

A faixa teórica vai de `-1020`, quando o centro vale 255 e os vizinhos valem 0, a
`+1020` no caso oposto. Na imagem real observou-se de `-415` a `+345`.

O número que importa é este: 47,0% dos pixels da resposta ficam fora da faixa de
8 bits, e 143851 são negativos. Guardar o Laplaciano direto em `uint8`
descartaria quase metade da informação. Além de perder a análise, isso quebraria
o realce, que subtrai a resposta da imagem original e depende justamente da
parte negativa.

O comportamento numa transição também explica por que o sinal importa. No degrau
vertical sintético, a resposta vale `+255` de um lado e `-255` do outro, com 16
posições de cada sinal, e passa por zero entre eles. É o cruzamento por zero
descrito no material. Com valor absoluto aplicado cedo, os dois lados ficariam
idênticos e essa estrutura desapareceria.

### 7.6 Diferença entre Gx e Gy no Sobel

`Gx` compara o lado direito com o esquerdo da vizinhança, portanto mede a
variação ao longo de x e evidencia bordas verticais. `Gy` compara a parte
inferior com a superior, mede a variação ao longo de y e evidencia bordas
horizontais.

Os casos sintéticos separam os dois de forma exata. No degrau vertical, `Gx`
chega a 1020 e `Gy` é identicamente zero em toda a imagem. No degrau horizontal,
o oposto. Não é aproximadamente zero: é zero, porque as contribuições de cima e
de baixo se cancelam.

Vale registrar a confusão comum, listada como erro frequente no material: `Gx`
não detecta bordas horizontais. Ele mede variação horizontal, e uma variação
horizontal indica uma borda vertical.

O sinal também carrega informação. Invertendo a transição, de clara para escura,
`Gx` troca de sinal e a magnitude permanece, o que é verificado em
`test_transicao_invertida_inverte_o_sinal_e_mantem_a_magnitude`. Aplicar valor
absoluto cedo perderia o sentido da transição.

Numa borda diagonal, as duas componentes respondem, e é por isso que faz sentido
combiná-las numa magnitude.

### 7.7 Diferenças entre |Gx| + |Gy| e sqrt(Gx² + Gy²)

As duas medem a mesma coisa, a força da transição, em escalas diferentes. Vale
sempre `L1 >= L2`, com igualdade quando uma das componentes é zero.

A razão entre elas depende da orientação do gradiente. Quando ele está alinhado
a um eixo, as duas coincidem. Quando está a 45 graus, `L1` é `raiz de 2` vezes
maior. Na imagem real, a razão média medida foi 1,2666, entre os dois extremos,
como esperado de uma imagem com bordas em várias orientações.

Isso tem consequência prática na saturação. Com `clamp` em 255, `L1` satura
29204 pixels, ou 9,54% da imagem, e `L2` satura 18339, ou 5,99%. `L1` satura 59%
mais pixels que `L2` sobre exatamente a mesma imagem. Os máximos também diferem,
1230 contra 934,26.

A conclusão é que um limiar escolhido para uma métrica não pode ser reaproveitado
na outra. Um limiar de 200 sobre `L1` seleciona um conjunto de bordas
sensivelmente maior que o mesmo 200 sobre `L2`.

`L1` é mais barata, por evitar duas multiplicações e uma raiz quadrada, e é uma
aproximação razoável quando só interessa ordenar bordas por força. `L2` é a
magnitude geométrica correta do vetor gradiente, e é a escolha quando o valor
precisa ter significado métrico ou ser comparado entre imagens.

## 8. Limitações

- A implementação calcula correlação, não convolução matemática estrita. Para os
  kernels simétricos usados nas suavizações isso é indiferente, mas para Sobel
  os sinais seriam invertidos na outra convenção. A convenção está declarada,
  como o material exige, e não há opção de girar o kernel.
- A estratégia `replicate` extrapola dados que não existem. Ela produz uma
  imagem completamente filtrada, mas a periferia é influenciada por valores
  artificiais. Estratégias de reflexão, que reduziriam a descontinuidade, não
  fazem parte do mínimo obrigatório e não foram implementadas.
- O Laplaciano é sensível a ruído, por ser derivada de segunda ordem. A
  combinação com suavização gaussiana prévia, o Laplaciano do Gaussiano, não foi
  implementada como operação própria, embora possa ser obtida encadeando
  `weighted_mean` e `laplacian` pela linha de comando.
- A direção do gradiente, `atan2(Gy, Gx)`, não é calculada. O enunciado pede as
  componentes e as duas magnitudes, e a direção não consta entre elas.
- As imagens de visualização não contêm os valores brutos. Comparações
  numéricas devem usar os arquivos em `results/`, não os arquivos PNG. O modo
  `normalize`, em particular, impede comparação absoluta entre execuções, porque
  a escala depende da faixa observada em cada imagem.
- O percurso explícito, sem vetorização, custa 4,4 segundos para o conjunto
  completo nesta imagem de 306 mil pixels. A restrição vem do enunciado, que
  exige implementação manual.
- A análise de custo da seção 7.3 mede tempo de parede em uma única execução,
  sem repetição nem controle de variação da máquina. Serve para comparar ordens
  de grandeza, não como benchmark.

## 9. Declaração de uso de IA

Houve uso de IA generativa. Os detalhes estão em [AI_USAGE.md](AI_USAGE.md).

## 10. Referências

- Enunciado do laboratório: [laboratorio_M1_3.md](laboratorio_M1_3.md)
- Material de apoio da disciplina: [encontro_04_dominio_espacial.md](encontro_04_dominio_espacial.md), [bordas.md](bordas.md), [filtro_laplaciano.md](filtro_laplaciano.md), [filtro_sobel.md](filtro_sobel.md)
- Contrato técnico dos laboratórios da M1: `lab_tecnico.md`, na raiz do
  repositório
- Rubrica geral: `rubrica_avaliativa.md`, na raiz do repositório
- Documentação do OpenCV sobre leitura e escrita de imagens, módulo `imgcodecs`
