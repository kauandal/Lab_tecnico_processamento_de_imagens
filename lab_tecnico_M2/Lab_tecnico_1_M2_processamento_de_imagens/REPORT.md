# Relatório técnico M2.1

## 1. Identificação

- Estudante: Kauan Rocha Dalfovo
- Laboratório: M2.1, máscara binária e segmentação
- Disciplina: Processamento de Imagens, 2026-02
- Linguagem: Python 3.13.14, com numpy 2.5.2 e opencv-python 5.0.0.93

## 2. Objetivo

Gerar uma máscara binária de moedas, comparar um limiar fixo em cinza com o
método de Otsu nas mesmas imagens e escolher a máscara que segue para o M2.2,
apontando os acertos e os erros de cada configuração.

## 3. Operações implementadas

| Método | Função | Saídas geradas |
|---|---|---|
| `fixed` | `threshold_fixed` | `coins_mask_fixed.png`, `moedas_brasileiras_mask_fixed.png` |
| `otsu` | `threshold_otsu` | `coins_mask_otsu.png`, `moedas_brasileiras_mask_otsu.png` |
| `adaptive` | `threshold_adaptive` | disponível, não usado no estudo |
| `hsv` | `hsv_range` | disponível, não usado no estudo |
| sobreposição | `overlay` | `*_overlay_fixed.png`, `*_overlay_otsu.png` |
| validação | `validate_mask` | conferida em toda máscara gravada |

Todas estão em `src/pdi_lab/segmentation.py`. A limiarização usa as funções
do OpenCV, como o enunciado permite.

## 4. Decisões de implementação

### 4.1 Alvo e imagens

O alvo é a moeda. Cada moeda inteira é um objeto, e todo o resto é fundo. Na
máscara, 255 é moeda e 0 é fundo.

| Imagem | Papel | Motivo |
|---|---|---|
| `coins.png` | dificuldade real | o fundo tem tons de cinza parecidos com os das moedas e fica mais claro no topo |
| `moedas_brasileiras.jpg` | condição favorável | fundo branco uniforme e cinco moedas separadas |

As duas têm mais de um objeto: 24 moedas em `coins.png` e 5 em
`moedas_brasileiras.jpg`. Os originais não foram alterados.

### 4.2 Regra do limiar fixo

O objeto é o pixel com cinza maior que o limiar. O pixel igual ao limiar vai
para o fundo, que é o comportamento do `THRESH_BINARY` do OpenCV. O teste
`test_limiar_fixo_no_limiar_e_dos_dois_lados` fixa essa regra com os valores
119, 120 e 121.

Imagens coloridas são convertidas para cinza antes do limiar.

### 4.3 Inversão

Em `moedas_brasileiras.jpg` as moedas são mais escuras que o fundo. Sem
inversão, a máscara marcaria o fundo branco como objeto. Por isso as duas
configurações dessa imagem usam `--invert`. Em `coins.png` as moedas são mais
claras que o fundo e não há inversão.

### 4.4 Pré-processamento

Nenhuma das configurações comparadas usa pré-processamento, então a diferença
entre as máscaras vem só do método e do limiar.

Foi testado o Otsu com suavização gaussiana 5 x 5 em `coins.png`. O limiar
calculado foi 104 e a proporção de primeiro plano subiu de 38,8% para 41,3%.
Os pontos isolados diminuíram, mas mais fundo passou a ser marcado como
moeda, então a suavização não foi usada.

### 4.5 Validação da máscara

A máscara é conferida duas vezes: na matriz gerada e no arquivo relido do
disco. A conferência verifica as dimensões da entrada, um canal, tipo `uint8`
e valores só em {0, 255}. A saída em JPEG é recusada, porque a compressão cria
valores intermediários.

### 4.6 Guardas

| Situação | Comportamento |
|---|---|
| arquivo inexistente ou que não é imagem | erro explicativo, código de saída 1 |
| método ou operação desconhecidos | código de saída 2, tratado pelo `argparse` |
| `fixed` sem `--threshold` ou limiar fora de 0 a 255 | erro explicativo |
| `--blur` ou `--block-size` par | erro explicativo |
| `adaptive` sem `--c` | erro explicativo |
| `hsv` sem limites, com H acima de 179 ou em imagem cinza | erro explicativo |
| saída `.jpg`, `.jpeg` ou `.webp` | erro explicativo, nenhum arquivo gravado |
| máscara com valor fora de {0, 255} ou tamanho diferente | erro explicativo |

## 5. Testes realizados

`python -m pytest` executa 69 testes, todos aprovados.

Cobertura por tipo:

- imagem sintética com pixels abaixo do limiar, no limiar e acima dele, para
  o limiar fixo e para a inversão;
- Otsu em imagem com dois tons, adaptativo com C positivo e negativo e HSV
  com faixa que passa pelo 179 e volta ao 0;
- validação de dimensões, canal único, tipo e valores {0, 255};
- todas as guardas listadas na seção anterior;
- códigos de saída 0, 1 e 2 pela linha de comando;
- as duas imagens reais nas duas configurações, com uma limitação conferida
  em cada uma: o fundo do topo marcado como moeda em `coins.png` e o Otsu
  perdendo o interior das moedas em `moedas_brasileiras.jpg`.

## 6. Resultados

Parâmetros das duas configurações:

| Imagem | Limiar fixo | Otsu |
|---|---|---|
| `coins.png` | `--threshold 120` | limiar calculado 107 |
| `moedas_brasileiras.jpg` | `--threshold 230 --invert` | limiar calculado 188, com `--invert` |

Proporção de primeiro plano, de `results/foreground.csv`:

| Imagem | Configuração | Limiar | Pixels de moeda | Proporção |
|---|---|---:|---:|---:|
| `coins.png` | fixed | 120 | 38336 | 32,9% |
| `coins.png` | otsu | 107 | 45117 | 38,8% |
| `moedas_brasileiras.jpg` | fixed + invert | 230 | 54543 | 27,3% |
| `moedas_brasileiras.jpg` | otsu + invert | 188 | 32198 | 16,1% |

Todas as máscaras passaram na validação da seção 4.5.

Figura 1, `images/output/coins_comparacao.png`: original, limiar fixo, Otsu e
sobreposição do limiar fixo.

![coins](images/output/coins_comparacao.png)

Figura 2, `images/output/moedas_brasileiras_comparacao.png`: original, limiar
fixo, Otsu e sobreposição do limiar fixo.

![moedas brasileiras](images/output/moedas_brasileiras_comparacao.png)

Na sobreposição, verde é o que foi marcado como moeda e vermelho é o contorno
da máscara. Contorno vermelho dentro de uma moeda indica um furo.

Configuração escolhida para o M2.2: limiar fixo nas duas imagens.

- `coins.png`: as duas configurações marcam a faixa clara do topo como moeda,
  mas o Otsu piora esse erro. Nas 25 primeiras linhas, que são só fundo, o
  Otsu marca 61,7% dos pixels e o limiar fixo marca 34,6%. Com o Otsu a faixa
  também chega perto da primeira moeda de cima, e as duas podem virar uma
  região só. Em troca, o limiar fixo deixa mais furos nas moedas escuras.
- `moedas_brasileiras.jpg`: o limiar fixo pega as cinco moedas quase
  inteiras. O Otsu marca só os relevos e as bordas.

Erros visíveis na configuração escolhida:

| Imagem | Falsos positivos | Falsos negativos |
|---|---|---|
| `coins.png` | faixa clara do fundo no topo, encostada na borda | furos nas moedas de relevo escuro, principalmente na linha de baixo |
| `moedas_brasileiras.jpg` | pontos soltos perto da borda das moedas, por causa da compressão JPEG | furos onde o relevo é muito claro, nas moedas de 25 e 10 centavos |

A proporção de primeiro plano é só uma contagem sobre a máscara. Sem máscara
de referência ela não mede acerto, por isso este relatório não declara
acurácia, precisão nem revocação. Os acertos e erros acima são observações
visuais.

## 7. Análise técnica

### 7.1 Em que casos o limiar fixo falhou ou funcionou

Funcionou em `moedas_brasileiras.jpg`. O fundo é branco e uniforme e
nenhuma moeda chega ao branco, então qualquer limiar entre 220 e 240 dá uma
máscara parecida, com proporção entre 25,1% e 28,7%.

Falhou em parte em `coins.png`, porque o brilho do fundo muda ao longo da
imagem. Um limiar baixo o bastante para preencher as moedas escuras também
marca o fundo claro do topo, e um limiar alto o bastante para limpar o topo
esvazia as moedas escuras. O Otsu também é um limiar global e não resolve.

O Otsu falhou em `moedas_brasileiras.jpg` por outro motivo: mais da metade da
imagem é fundo branco, com mediana do cinza igual a 255, e o limiar
calculado, 188, acabou separando os tons de dentro das moedas.

### 7.2 Qual parâmetro foi mais sensível

O limiar em `coins.png`. Em `results/threshold_sensitivity.csv`, a proporção
cai de 47,4% com limiar 90 para 20,4% com limiar 150, cerca de 2,3 pontos
percentuais a cada 5 níveis de cinza. Em `moedas_brasileiras.jpg`, entre 220
e 250 a variação total é de 5,2 pontos, porque o fundo está em 255 e não muda
de lado.

A inversão também decide o resultado, mas é uma escolha e não um ajuste: sem
ela a máscara de `moedas_brasileiras.jpg` marcaria o fundo.

### 7.3 Quais erros podem atrapalhar a contagem no M2.2

- A faixa do topo de `coins.png` é grande e vai ser contada como objeto. Um
  filtro por área mínima não a remove, porque ela é maior que as moedas.
- Os furos sozinhos não mudam a contagem, mas uma moeda com muitos furos pode
  se partir em pedaços e ser contada mais de uma vez. O fechamento deve
  ajudar nesse caso.
- Os pontos soltos geram componentes pequenos que aumentam a contagem bruta.
  A abertura ou um filtro por área mínima devem tratar isso.
- Nenhuma das imagens tem moedas encostadas, então o caso de duas moedas
  virarem um componente só não aparece neste par.

## 8. Limitações

- A fonte original e a licença de `moedas_brasileiras.jpg` ainda não foram
  verificadas.
- Não há máscara de referência. As observações sobre acertos e erros são
  visuais.
- Os limiares fixos, 120 e 230, foram escolhidos olhando as sobreposições,
  com apoio da varredura em `results/threshold_sensitivity.csv`, e não por um
  critério automático.
- Os métodos `adaptive` e `hsv` estão implementados e testados, mas não fazem
  parte da comparação principal. Em `coins.png` o adaptativo deixou as moedas
  ocas, e em `moedas_brasileiras.jpg` o HSV por saturação perdeu as partes
  prateadas, que quase não têm saturação.

## 9. Declaração de uso de IA

Houve uso de IA generativa. Os detalhes estão em [AI_USAGE.md](AI_USAGE.md).

## 10. Referências

- Enunciado do laboratório: [laboratorio_1_M2.md](laboratorio_1_M2.md)
- Contrato técnico dos laboratórios da M1: `lab_tecnico.md`, em
  `lab_tecnico_M1/`
- Rubrica geral: `rubrica_avaliativa.md`, em `lab_tecnico_M1/`
- Documentação do OpenCV sobre limiarização, funções `threshold` e
  `adaptiveThreshold`
- Documentação do scikit-image sobre o conjunto de dados `skimage.data`, de
  onde vem `coins.png`
