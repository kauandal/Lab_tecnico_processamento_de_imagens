# Processamento de Imagens — 2026-02
## Laboratório M1.3 — Convolução e filtragem espacial

## Objetivo

Implementar operações de vizinhança e convolução no domínio espacial, tratando explicitamente kernels, bordas, tipos numéricos e saturação.

Neste laboratório, o valor de cada pixel de saída depende de uma vizinhança da imagem de entrada.

## Regras específicas

A convolução, o percurso das vizinhanças e o tratamento das bordas devem ser implementados manualmente.

Não utilize funções prontas que realizem diretamente:

- convolução;
- filtros de média;
- Laplaciano;
- Sobel;
- tratamento automático equivalente das bordas.

Funções prontas podem ser utilizadas somente para comparação e validação, quando claramente separadas da implementação avaliada.

## Atividades obrigatórias

### 1. Convolução genérica

Implemente uma função capaz de receber:

- uma imagem em níveis de cinza;
- um kernel quadrado;
- um kernel de dimensão ímpar;
- a estratégia de tratamento de borda.

O percurso deve considerar corretamente o centro do kernel e sua vizinhança.

### 2. Tratamento de bordas

Implemente pelo menos duas estratégias:

1. **copiar/ignorar:** pixels onde a vizinhança não cabe integralmente mantêm o valor original ou não são processados;
2. **replicar:** coordenadas fora da imagem são substituídas pela coordenada válida mais próxima.

Compare os efeitos nas regiões periféricas.

### 3. Filtros de suavização

Aplique:

- média `3 × 3`;
- média ponderada `3 × 3`;
- média `5 × 5`.

Compare suavização, perda de detalhes e custo relativo.

### 4. Laplaciano e realce

Aplique um kernel Laplaciano.

Registre a resposta antes da conversão final para visualização, considerando que ela pode conter valores negativos.

Produza também uma imagem realçada pela combinação da resposta com a imagem original.

### 5. Sobel

Calcule:

- `Gx`;
- `Gy`;
- magnitude aproximada `|Gx| + |Gy|`;
- magnitude euclidiana `sqrt(Gx² + Gy²)`.

Mantenha tipos numéricos adequados durante os cálculos e realize saturação apenas quando necessário para produzir a imagem final.

## Testes mínimos

Inclua:

- kernel identidade;
- imagem constante;
- imagem impulso;
- degrau vertical;
- degrau horizontal;
- formas geométricas simples;
- imagem com conteúdo tocando as bordas;
- kernel `3 × 3`;
- kernel `5 × 5`.

Os casos sintéticos devem permitir prever o comportamento esperado antes da execução.

## Resultados esperados

- O kernel identidade deve reproduzir a imagem.
- O filtro de média deve reduzir variações locais e também detalhes.
- A resposta do Laplaciano deve ser forte em transições e pode conter valores negativos antes da visualização.
- `Gx` deve responder principalmente a bordas verticais.
- `Gy` deve responder principalmente a bordas horizontais.
- As estratégias de borda devem produzir diferenças principalmente nas regiões periféricas.

## Análise

No mini relatório, responda objetivamente:

1. Qual é a diferença entre uma operação pontual e uma operação de vizinhança?
2. Por que kernels normalmente possuem dimensões ímpares?
3. Qual é o efeito de aumentar o tamanho do kernel de média?
4. Como a estratégia de tratamento de bordas interfere no resultado?
5. Por que a resposta bruta do Laplaciano pode conter valores negativos?
6. Qual é a diferença entre `Gx` e `Gy` no Sobel?
7. Que diferenças são observadas entre `|Gx| + |Gy|` e `sqrt(Gx² + Gy²)`?

## Guardas esperadas

Considere, quando pertinente:

- falha na leitura da imagem;
- kernel vazio;
- kernel não quadrado;
- kernel de dimensão par;
- acesso fora dos limites;
- estratégia de borda inválida;
- acumuladores com valores negativos;
- valores maiores que 255;
- conversões numéricas;
- saturação apenas no momento apropriado.

## Entrega

Entregue:

- código-fonte;
- instruções de execução;
- imagens utilizadas;
- imagens de saída;
- parâmetros e kernels utilizados;
- testes;
- mini relatório;
- declaração de uso ou não de IA generativa.

A evidência parcial e a versão consolidada seguem as regras da rubrica geral dos laboratórios da M1.