# Processamento de Imagens — 2026-02
## Laboratório M1.1 — Representação, canais e níveis de cinza

## Objetivo

Implementar operações fundamentais de representação de imagens digitais por meio de acesso direto aos pixels, relacionando dimensões, canais, intensidade e resolução radiométrica.

## Regras específicas

As operações solicitadas devem ser implementadas manualmente, com percurso explícito dos pixels.

Não utilize funções prontas que realizem diretamente:

- cópia integral da imagem;
- separação de canais;
- conversão para níveis de cinza;
- quantização.

Bibliotecas podem ser utilizadas para leitura, escrita, criação de matrizes e acesso aos pixels.

## Atividades obrigatórias

Desenvolva um programa que receba uma imagem e execute as seguintes operações.

### 1. Inspeção da imagem

Informe:

- largura;
- altura;
- número de canais;
- tipo da imagem;
- quantidade de pixels;
- valor mínimo;
- valor máximo;
- média das intensidades.

Para imagens coloridas, apresente mínimo, máximo e média por canal.

### 2. Cópia manual

Crie uma nova imagem e copie todos os pixels individualmente.

A saída deve ser numericamente idêntica à entrada.

### 3. Separação manual dos canais

Gere três imagens:

- canal azul;
- canal verde;
- canal vermelho.

Em cada imagem, preserve somente o canal correspondente e zere os demais.

### 4. Conversão manual para níveis de cinza

Implemente duas versões.

**Média simples:**

$$
g = \frac{R + G + B}{3}
$$

**Média ponderada:**

$$
g = 0,299R + 0,587G + 0,114B
$$

Compare os resultados.

### 5. Quantização

A partir de uma imagem em níveis de cinza, produza versões com:

- 16 níveis;
- 8 níveis;
- 4 níveis;
- 2 níveis.

Os valores resultantes devem permanecer no intervalo válido da imagem.

## Saídas mínimas

Sugestão de nomes:

```text
copy.png
channel_b.png
channel_g.png
channel_r.png
gray_average.png
gray_weighted.png
quant_16.png
quant_8.png
quant_4.png
quant_2.png
```

Os nomes podem variar desde que estejam claramente documentados.

## Testes mínimos

Utilize as imagens fornecidas e inclua pelo menos um caso pequeno ou sintético que permita conferência manual.

Os testes devem permitir verificar:

- cópia exata dos pixels;
- ordem dos canais;
- cálculo das duas versões em níveis de cinza;
- quantidade de níveis após a quantização;
- comportamento em valores próximos aos limites.

## Análise

No mini relatório, responda objetivamente:

1. Qual é a diferença entre resolução espacial e resolução radiométrica?
2. Por que a média ponderada produz resultado diferente da média simples?
3. O que ocorre visualmente quando a quantidade de níveis é reduzida?
4. Em quais regiões da imagem a perda de informação fica mais evidente?
5. Como o tipo e o número de canais da imagem interferem na forma de acessar um pixel?

## Guardas esperadas

Considere, quando pertinente:

- falha na leitura da imagem;
- número inesperado de canais;
- tipo de imagem incompatível com a operação;
- arredondamento;
- valores fora do intervalo permitido;
- quantidade inválida de níveis de quantização.

## Entrega

Entregue:

- código-fonte;
- instruções de execução;
- imagens utilizadas;
- imagens de saída;
- testes;
- mini relatório;
- declaração de uso ou não de IA generativa.

A evidência parcial e a versão consolidada seguem as regras da rubrica geral dos laboratórios da M1.