# Processamento de Imagens — 2026-02
## Rubrica geral dos Laboratórios da M1

Os três laboratórios da M1 são atividades individuais e serão avaliados pelos mesmos cinco critérios gerais: **Execução, Aquisição e requisitos, Corretude, Guardas e Análise**.

A escolha da linguagem entre C++, Java e Python não altera os objetivos técnicos nem o rigor da avaliação. Quando o enunciado exigir implementação manual, não é permitido substituir a operação por uma função pronta equivalente.

## Composição da nota

- **Evidência parcial de desenvolvimento:** 15% da nota do laboratório.
- **Versão consolidada:** 85% da nota do laboratório, avaliada pelos cinco critérios abaixo.

A ausência da evidência parcial limita a nota máxima do laboratório a **8,5**, sem aplicação de penalização adicional pelo mesmo motivo.

## Critérios da versão consolidada

| Critério | Peso na versão consolidada | O que será avaliado |
|---|---:|---|
| Execução | 20% | Compilação/execução, geração das saídas e possibilidade de reprodução. |
| Aquisição e requisitos | 20% | Interpretação e atendimento dos requisitos, entradas, parâmetros, formatos e artefatos solicitados. |
| Corretude | 30% | Correção dos algoritmos, cálculos, percursos e resultados. |
| Guardas | 15% | Tratamento de entradas inválidas, limites, saturação, tipos, bordas e demais casos especiais pertinentes. |
| Análise | 15% | Testes, comparação, interpretação de resultados, limitações e justificativas técnicas. |

## Descritores de desempenho

### Execução

**Excelente**  
O projeto compila ou executa pelo procedimento documentado, recebe as entradas sem necessidade de alteração do código, produz as saídas previstas e permite reprodução direta dos resultados.

**Adequado**  
Executa e produz os resultados principais, mas exige pequenos ajustes ou apresenta falhas secundárias de organização ou reprodução.

**Parcial**  
Somente parte relevante da atividade pode ser executada ou a reprodução exige intervenção significativa.

**Insuficiente**  
Não é possível executar a solução ou não há evidência verificável de funcionamento.

### Aquisição e requisitos

**Excelente**  
Interpreta e atende integralmente os requisitos do laboratório; utiliza corretamente entradas, imagens, parâmetros, formatos e artefatos solicitados.

**Adequado**  
Atende os requisitos principais, com pequenas omissões que não comprometem o objetivo central.

**Parcial**  
Atende apenas parte dos requisitos ou interpreta incorretamente elementos relevantes do enunciado.

**Insuficiente**  
Requisitos centrais não são atendidos ou a solução desenvolvida não corresponde ao problema solicitado.

### Corretude

**Excelente**  
Algoritmos, cálculos e resultados estão corretos e são confirmados por testes verificáveis.

**Adequado**  
Implementação essencialmente correta, com pequenas divergências localizadas.

**Parcial**  
Parte da solução funciona, mas há erros conceituais, algorítmicos ou numéricos relevantes.

**Insuficiente**  
A operação principal está incorreta, ausente ou foi substituída por recurso proibido quando a implementação manual era exigida.

### Guardas

**Excelente**  
Trata explicitamente as pré-condições, limites, tipos numéricos, saturação, bordas, dimensões, parâmetros inválidos e demais situações especiais pertinentes ao laboratório.

**Adequado**  
Trata as principais situações especiais, deixando poucos casos secundários descobertos.

**Parcial**  
Existem algumas verificações, mas casos previsíveis podem produzir resultados incorretos ou falhas.

**Insuficiente**  
Não há tratamento adequado das condições especiais relevantes.

### Análise

**Excelente**  
Apresenta testes controlados, interpreta os resultados, compara configurações quando solicitado, identifica limitações e relaciona as observações ao comportamento do algoritmo.

**Adequado**  
Apresenta resultados e análise coerente, porém com profundidade ou experimentação limitada.

**Parcial**  
Apresenta predominantemente descrição das saídas, com pouca interpretação ou evidência experimental.

**Insuficiente**  
Não apresenta análise técnica ou suas conclusões não são sustentadas pelos resultados.

## Evidência parcial de desenvolvimento

Na data prevista para cada laboratório, deverá ser entregue uma evidência técnica contendo, no mínimo:

- código em desenvolvimento;
- pelo menos uma execução registrada;
- pelo menos uma saída identificada;
- indicação breve do que já foi concluído e do que ainda falta.

A evidência parcial não é uma nota de presença ou participação. Ela registra o processo individual de desenvolvimento.

## Regras comuns

- A atividade é individual.
- C++, Java e Python são permitidos.
- O projeto final deve executar fora do Google Colab.
- Notebooks podem ser incluídos como material complementar, mas a lógica principal deve estar em arquivos-fonte da linguagem escolhida.
- Quando o enunciado exigir implementação manual, funções prontas equivalentes não podem substituir a implementação.
- As dependências utilizadas devem ser declaradas.
- As imagens fornecidas para teste devem ser preservadas.
- O uso de IA generativa é permitido, mas deve ser declarado de forma transparente.
- O estudante é responsável por compreender, testar e validar todo o conteúdo entregue.

## Entrega consolidada

A entrega deve conter, conforme aplicável ao laboratório:

- código-fonte;
- arquivos de configuração e dependências;
- `README.md` com instruções de compilação e execução;
- imagens de entrada;
- imagens de saída;
- resultados em CSV ou log, quando solicitados;
- testes;
- mini relatório técnico;
- declaração de uso ou não de IA generativa.

## Mini relatório

O mini relatório deve ser breve e baseado em evidências. Deve conter:

1. identificação do estudante e do laboratório;
2. objetivo;
3. operações implementadas;
4. decisões de implementação;
5. testes realizados;
6. resultados;
7. análise técnica;
8. limitações;
9. declaração de uso ou não de IA;
10. referências utilizadas.

## Declaração de IA

### Sem uso

> Declaro que não utilizei ferramentas de Inteligência Artificial generativa na elaboração do código, dos testes, das imagens, do relatório ou de outros artefatos deste laboratório.

### Com uso

Informar:

- ferramenta utilizada;
- finalidade;
- partes afetadas;
- forma de validação;
- modificações realizadas;
- link da conversa ou registro equivalente.

Quando não houver link compartilhável, deve ser entregue um registro equivalente que permita compreender as orientações recebidas e como foram utilizadas.