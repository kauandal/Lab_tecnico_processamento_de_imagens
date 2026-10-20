# Processamento de Imagens — 2026-02
## Rubrica dos laboratórios da M2

**Entrega final dos dois laboratórios: 20/10/2026.**

Os laboratórios são individuais e integram um único projeto de código:

- **M2.1 — Máscara binária e segmentação.**
- **M2.2 — Componentes conexos e sequência morfológica.**

As funções prontas do OpenCV são permitidas. A avaliação considera a aplicação dos métodos, os resultados, os testes e a capacidade de explicar as decisões. Não se exige implementar os algoritmos do OpenCV do zero. C++, Java e Python continuam permitidos, conforme o contrato técnico.

Esta rubrica organiza a avaliação dos requisitos já descritos nos enunciados e no contrato técnico. Não acrescenta operações ou artefatos obrigatórios à entrega final. **Somente o M2.1 teve relato parcial solicitado. O M2.2 não terá desconto por ausência de parcial.**

## 1 Composição das notas

Cada laboratório recebe uma nota de 0 a 10.

| Laboratório | Relato parcial | Versão final | Composição |
|---|---:|---:|---|
| M2.1 | 15% | 85% | Relato parcial já solicitado e entrega final da segmentação |
| M2.2 | Não exigido | 100% | Entrega final de componentes conexos e morfologia |

A versão final de cada laboratório é inicialmente avaliada em uma escala de 0 a 10, pelos cinco critérios da seção 2.

**M2.1:** `N1 = P + 0,85 × F1`

- `P = 1,50` quando o relato parcial solicitado foi entregue; `P = 0` quando sua ausência for confirmada.
- `F1` é a nota da versão final do M2.1, de 0 a 10.
- O relato é considerado conforme a solicitação feita na época. Não se exige retrospectivamente que ele contenha a solução final, todos os testes ou artefatos que ainda estavam em desenvolvimento.
- A ausência confirmada do relato limita o M2.1 a 8,50. Não há outro desconto pelo mesmo motivo.
- Um relato já entregue não precisa ser reenviado para ter seu registro reconhecido. Eventual dúvida no registro será conferida antes da atribuição de zero.

**M2.2:** `N2 = F2`

- `F2` é a nota da versão final do M2.2, de 0 a 10.
- Não existe parcela parcial nem teto de 8,50 no M2.2.

**Nota conjunta dos laboratórios:** `L = (N1 + N2) ÷ 2`.

Esta média corresponde ao conjunto dos laboratórios, não à média completa da M2, que também possui os demais instrumentos previstos na disciplina. Não arredonde valores intermediários; apresente as notas finais com duas casas decimais, observando a regra de lançamento do diário.

### Exemplos de cálculo

| Situação | F1 | P | N1 | F2 e N2 | Nota conjunta L |
|---|---:|---:|---:|---:|---:|
| Duas versões finais com nota máxima e relato entregue | 10,00 | 1,50 | 10,00 | 10,00 | 10,00 |
| Duas versões finais com nota máxima e relato ausente | 10,00 | 0,00 | 8,50 | 10,00 | 9,25 |
| Relato entregue e resultados finais distintos | 8,00 | 1,50 | 8,30 | 8,00 | 8,15 |

## 2 Critérios das versões finais

Os mesmos pesos se aplicam a `F1` e `F2`.

| Critério | Peso | Máximo na escala de 0 a 10 | Foco |
|---|---:|---:|---|
| Execução e reprodução | 20% | 2,00 | Preparar, executar e gerar resultados pelo procedimento documentado |
| Aquisição e atendimento dos requisitos | 20% | 2,00 | Atender operações, entradas, parâmetros, formatos e documentação solicitados |
| Corretude dos resultados | 30% | 3,00 | Produzir máscaras, contagens, medidas e transformações coerentes |
| Guardas e casos especiais | 15% | 1,50 | Tratar entradas inválidas e condições de limite pertinentes |
| Análise e justificativa técnica | 15% | 1,50 | Comparar resultados, justificar escolhas e reconhecer limitações |
| **Total da versão final** | **100%** | **10,00** | Soma dos cinco critérios |

### Escala de desempenho

| Nível | Parcela do máximo do critério | Interpretação |
|---|---:|---|
| Excelente | 100% | Atendimento completo, correto e sustentado por evidências verificáveis |
| Adequado | 75% | Atendimento dos elementos principais, com omissões ou falhas pontuais |
| Parcial | 50% | Parte relevante atendida, mas com lacunas que comprometem o resultado ou sua interpretação |
| Insuficiente | 25% | Evidência muito limitada, com falhas centrais e pouca possibilidade de verificação |
| Ausente ou sem evidência pertinente | 0% | O elemento não foi entregue ou não apresenta atendimento verificável ao critério |

Os valores são referências de correção. Pontuações intermediárias podem ser atribuídas com justificativa baseada nas evidências. Uma mesma entrega pode apresentar níveis diferentes nos cinco critérios.

## 3 Rubrica específica do M2.1

### 3.1 Execução e reprodução — 2,00 pontos

**Excelente:** o projeto prepara e executa localmente pelo `README.md`; a operação `segment` recebe imagem e parâmetros sem edição do código; as duas configurações podem ser reproduzidas nas imagens utilizadas; as saídas são gravadas nos caminhos informados.

**Adequado:** as configurações principais executam, com pequenos ajustes de documentação ou falhas secundárias de gravação ou organização.

**Parcial:** somente parte das configurações ou imagens pode ser processada, ou a reprodução exige intervenção significativa.

**Insuficiente:** há apenas execução isolada, dependente de ajustes não documentados, com pouca evidência de reprodução. Sem execução verificável, este critério recebe zero.

### 3.2 Aquisição e atendimento dos requisitos — 2,00 pontos

**Excelente:** define o alvo; utiliza pelo menos duas imagens com condições distintas; compara limiar fixo e pelo menos uma alternativa prevista; identifica métodos e parâmetros; entrega os arquivos solicitados e a documentação técnica e de uso de IA. Preserva as entradas e apresenta máscaras e visualização dos erros.

**Adequado:** atende ao núcleo do enunciado, com pequenas omissões de parâmetros, apresentação ou documentação.

**Parcial:** falta uma comparação importante, uma condição de imagem ou parte relevante dos artefatos solicitados.

**Insuficiente:** o atendimento é muito restrito, com alvo pouco definido e ausência de vários elementos centrais.

### 3.3 Corretude dos resultados — 3,00 pontos

**Excelente:** os métodos e seus parâmetros são aplicados corretamente; a máscara mantém as dimensões da entrada, possui um canal e valores 0/255; a polaridade é coerente com o alvo; a contagem ou proporção de primeiro plano confere com a máscara; os testes controlados confirmam o comportamento, inclusive no valor do limiar.

**Adequado:** resultados essencialmente corretos, com divergências pontuais que não comprometem a operação principal.

**Parcial:** parte da segmentação funciona, mas existem erros relevantes na comparação, na polaridade, no formato da máscara ou nos cálculos apresentados.

**Insuficiente:** as máscaras ou os cálculos pouco correspondem aos métodos declarados, com erros centrais. Operação ausente ou sem resultado pertinente recebe zero.

**Distinção para a correção:** uma máscara visualmente imperfeita em uma imagem difícil pode resultar de uma limitação do método. Se a operação está correta e a limitação é identificada, isso não equivale automaticamente a erro de implementação. A análise deve explicar o caso e a escolha da configuração de trabalho.

### 3.4 Guardas e casos especiais — 1,50 ponto

**Excelente:** trata falha de leitura, método desconhecido e parâmetros inválidos pertinentes à solução; verifica dimensões, canal e caráter binário da saída; informa erros claramente e retorna códigos de saída coerentes. Nas alternativas escolhidas, trata suas condições específicas de uso.

**Adequado:** trata os casos principais, com poucos casos secundários descobertos.

**Parcial:** realiza algumas verificações, mas entradas previsivelmente inválidas ainda causam falhas ou saídas enganosas.

**Insuficiente:** quase não há validação ou as mensagens não permitem identificar o problema.

Não se exige implementar guardas para métodos que o estudante não escolheu e que o enunciado não obrigou a oferecer.

### 3.5 Análise e justificativa técnica — 1,50 ponto

**Excelente:** compara configurações nas mesmas imagens, justifica o método escolhido para continuidade, registra parâmetros e eventual pré-processamento, aponta erros de inclusão e exclusão e explica seus efeitos na contagem posterior. Apresenta evidências visuais, dados de primeiro plano e limitações coerentes.

**Adequado:** apresenta comparação e escolha justificadas, mas com discussão ou evidência pouco aprofundada.

**Parcial:** descreve predominantemente as saídas, com pouca comparação ou ligação entre parâmetros e resultados.

**Insuficiente:** conclusões genéricas ou pouco sustentadas pelas imagens e testes. Sem análise pertinente, o critério recebe zero.

Métricas como precisão, revocação ou acurácia não são obrigatórias sem máscara de referência. A proporção de pixels brancos, isoladamente, não comprova qualidade de segmentação.

## 4 Rubrica específica do M2.2

### 4.1 Execução e reprodução — 2,00 pontos

**Excelente:** o mesmo projeto mantém `segment` e acrescenta `analyze`; a análise recebe uma máscara e produz saídas iniciais, intermediárias e finais; as conectividades e a sequência morfológica são reproduzíveis pelos argumentos ou configurações documentados.

**Adequado:** a análise principal executa, com pequenos ajustes de documentação ou falhas secundárias.

**Parcial:** apenas parte do fluxo executa, ou a reprodução das etapas exige intervenção significativa.

**Insuficiente:** existem apenas execuções isoladas, sem um fluxo de análise reproduzível. Sem execução verificável, este critério recebe zero.

### 4.2 Aquisição e atendimento dos requisitos — 2,00 pontos

**Excelente:** usa a máscara do M2.1; compara conectividades 4 e 8 na mesma máscara; aplica pelo menos duas operações morfológicas em sequência, incluindo abertura ou fechamento; registra elemento estruturante, iterações e ordem; entrega imagens intermediárias, CSV de componentes, resumo e comparação antes/depois nas imagens solicitadas.

**Adequado:** atende os elementos centrais, com pequenas omissões de registro, formato ou documentação.

**Parcial:** falta uma comparação, uma etapa morfológica ou parte relevante das medidas e saídas previstas.

**Insuficiente:** há apenas rotulação ou morfologia isolada, sem atender à integração e às evidências centrais do enunciado.

Watershed, contornos e classificação são extensões opcionais. Sua ausência não gera desconto, e sua presença não substitui os requisitos obrigatórios.

### 4.3 Corretude dos resultados — 3,00 pontos

**Excelente:** a conectividade está correta; o fundo é excluído da contagem; áreas, caixas e centroides são consistentes com a máscara; a sequência morfológica corresponde às operações e parâmetros declarados; as contagens e áreas antes/depois conferem com as saídas. Se houver filtro por área, distingue resultados brutos dos filtrados e aplica o critério declarado.

**Adequado:** o fluxo é essencialmente correto, com divergências localizadas nas medidas, exportações ou comparações.

**Parcial:** parte do fluxo funciona, mas existem erros relevantes de conectividade, contagem, medidas ou sequência de operações.

**Insuficiente:** os resultados centrais são incoerentes com as máscaras ou com as operações informadas. Operação ausente ou sem resultado pertinente recebe zero.

A soma das áreas dos componentes brutos deve corresponder ao número de pixels de primeiro plano da máscara respectiva. Não se exige coincidência dos números dos rótulos entre bibliotecas ou execuções equivalentes. Objetos em contato podem formar um único componente sem que isso constitua erro da rotulação.

### 4.4 Guardas e casos especiais — 1,50 ponto

**Excelente:** trata máscara inexistente ou incompatível, conectividade inválida, parâmetros morfológicos inválidos e filtro de área inválido, quando oferecido; lida corretamente com máscara sem objetos e com conteúdo na borda; produz mensagens claras e códigos de saída coerentes.

**Adequado:** trata as principais condições, com poucas lacunas secundárias.

**Parcial:** há verificações, mas casos previsíveis provocam falhas ou cálculos inadequados.

**Insuficiente:** quase não há tratamento, ou casos como máscara vazia comprometem o fluxo.

### 4.5 Análise e justificativa técnica — 1,50 ponto

**Excelente:** explica diferenças ou coincidências entre conectividades, justifica a finalidade e a ordem de cada operação morfológica, compara o antes/depois e discute ao menos um benefício e um efeito indesejado ou limitação. Relaciona medidas, imagens e interpretação humana da contagem.

**Adequado:** as escolhas e comparações são coerentes, mas a discussão dos efeitos ou limites é pouco aprofundada.

**Parcial:** descreve operações e números sem justificar suficientemente as escolhas ou as mudanças observadas.

**Insuficiente:** há pouca relação entre conclusões e resultados. Sem análise pertinente, o critério recebe zero.

Não se exige que a morfologia melhore todos os casos. Identificar e explicar uma perda de detalhe, uma fusão de objetos ou uma separação não resolvida faz parte da análise.

## 5 Organização da entrega final

Entregue uma versão consolidada do único projeto, contendo os elementos já previstos nos enunciados e no contrato:

- fontes e arquivos de dependências ou compilação;
- `README.md` com os comandos de execução das duas etapas;
- `REPORT.md` com seções M2.1 e M2.2;
- `AI_USAGE.md` e `lab.json`;
- imagens originais, máscaras, resultados intermediários e saídas finais;
- tabelas, CSV, resumos e testes pertinentes a cada etapa.

O relato parcial do M2.1 é conferido no registro da entrega anterior. **Não é solicitado relato parcial do M2.2.** Caso o ambiente possua campos separados para as entregas finais, identifique claramente o mesmo projeto consolidado e os resultados de cada laboratório.

A solução deve executar localmente fora do Colab. Notebooks podem acompanhar a entrega como material complementar. Preserve as regras do contrato sobre caminhos, parâmetros, dependências e exclusão de binários gerados, ambientes virtuais e caches.

## 6 Regras para uma correção consistente

- Cada desconto deve indicar o critério, a evidência e a falha observada. Não há descontos adicionais sem previsão nas orientações da atividade.
- A falta do relato do M2.1 afeta somente sua parcela de 1,50 ponto. Não afeta o M2.2 e não reduz novamente os critérios da versão final.
- Uma falha de execução não zera automaticamente toda a atividade. Os demais critérios podem receber crédito por evidências verificáveis, com os limites de validação registrados.
- Um defeito único não gera descontos repetidos sem justificativa. Se produzir efeitos diferentes, a correção deve explicar a distinção entre os requisitos ausentes, os resultados incorretos e a análise insuficiente.
- O M2.2 pode ser verificado também com uma máscara de teste compatível com o enunciado, para distinguir um problema da segmentação anterior de um problema da análise de componentes.
- Arquivos e infraestrutura compartilhados são verificados uma vez; a nota de cada lab considera o atendimento e os resultados da sua etapa.
- O uso declarado de OpenCV ou IA generativa não reduz a nota por si só. O estudante continua responsável pela compreensão, validação, referências e transparência do material entregue.

## 7 Registro da avaliação

**Estudante:** ____________________

| Critério | Máximo | F1 obtido | F2 obtido |
|---|---:|---:|---:|
| Execução e reprodução | 2,00 | | |
| Aquisição e requisitos | 2,00 | | |
| Corretude | 3,00 | | |
| Guardas | 1,50 | | |
| Análise | 1,50 | | |
| **Nota da versão final** | **10,00** | | |

**Relato parcial do M2.1:** entregue / ausência confirmada / registro a conferir.

**P:** ______ / 1,50.

**N1 = P + 0,85 × F1:** ______ / 10,00.

**N2 = F2:** ______ / 10,00.

**Nota conjunta L = (N1 + N2) ÷ 2:** ______ / 10,00.

**Justificativas e orientações prioritárias:**

____________________________________________________________________