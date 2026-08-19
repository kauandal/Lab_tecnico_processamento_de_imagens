# Processamento de Imagens — 2026-02
## Laboratório M1.2 — Transformações de intensidade

## Objetivo

Implementar transformações pontuais em imagens em níveis de cinza e analisar como essas operações alteram os valores dos pixels e a distribuição das intensidades.

Neste laboratório, cada pixel de saída depende apenas do pixel correspondente da imagem de entrada.

## Regras específicas

As transformações devem ser implementadas manualmente, com percurso explícito dos pixels.

Não utilize funções prontas que realizem diretamente:

- ajuste de brilho;
- ajuste de contraste;
- negativo;
- limiarização;
- cálculo do histograma.

Bibliotecas podem ser utilizadas para leitura, escrita, criação de matrizes e acesso aos pixels.

## Atividades obrigatórias

### 1. Ajuste de brilho

Implemente:

$$
g(x,y) = f(x,y) + b
$$

Realize pelo menos:

- um teste com `b < 0`;
- um teste com `b > 0`.

Valores resultantes devem ser limitados ao intervalo válido da imagem.

### 2. Ajuste de contraste

Implemente:

$$
g(x,y) = \alpha(f(x,y)-128)+128
$$

Teste, no mínimo:

- `α = 0,5`;
- `α = 1,0`;
- `α = 1,5`.

### 3. Negativo

Implemente:

$$
g(x,y) = 255 - f(x,y)
$$

Aplique a operação a uma imagem em níveis de cinza.

### 4. Limiarização binária

Implemente:

$$
g(x,y)=
\begin{cases}
0, & f(x,y) < T \\
255, & f(x,y) \ge T
\end{cases}
$$

Teste pelo menos dois valores distintos de `T` na mesma imagem.

### 5. Histograma manual

Crie uma estrutura com 256 posições e contabilize quantos pixels possuem cada intensidade.

Registre o resultado em CSV ou formato textual equivalente.

Exemplo:

```text
intensidade,quantidade
0,12
1,7
2,19
...
255,3
```

Calcule o histograma:

- da imagem original;
- de pelo menos duas imagens transformadas.

## Atividades complementares

Estas atividades são opcionais e não substituem as obrigatórias:

- seleção por intervalo `[Tmin, Tmax]`;
- expansão linear de contraste;
- transformação gama.

## Testes mínimos

Utilize as imagens fornecidas e pelo menos uma imagem pequena ou sintética que permita conferir resultados manualmente.

Os testes devem incluir:

- brilho negativo e positivo;
- contraste reduzido, identidade e ampliado;
- negativo;
- dois valores de limiar;
- caso que provoque saturação;
- histograma antes e depois de transformações.

## Análise

No mini relatório, responda objetivamente:

1. Qual é a diferença observada entre alteração de brilho e alteração de contraste?
2. Em quais testes ocorreu saturação e qual foi seu efeito?
3. Como o histograma se deslocou após alterar o brilho?
4. Como a distribuição das intensidades mudou ao alterar o contraste?
5. Que informação é perdida após a limiarização?

## Guardas esperadas

Considere, quando pertinente:

- falha na leitura da imagem;
- imagem incompatível com a operação;
- parâmetros inválidos;
- valores menores que 0;
- valores maiores que 255;
- conversões entre tipos inteiros e ponto flutuante;
- arredondamento;
- limiar fora do intervalo esperado.

## Entrega

Entregue:

- código-fonte;
- instruções de execução;
- imagens utilizadas;
- imagens de saída;
- histogramas;
- testes;
- mini relatório;
- declaração de uso ou não de IA generativa.

A evidência parcial e a versão consolidada seguem as regras da rubrica geral dos laboratórios da M1.
