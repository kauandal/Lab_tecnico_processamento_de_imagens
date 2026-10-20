# Processamento de Imagens — 2026-02
## Contrato técnico dos Laboratórios da M1 — versão para estudantes

Este documento apresenta as regras técnicas comuns aos três laboratórios individuais da M1.

O objetivo é garantir que projetos desenvolvidos em **C++, Java ou Python** possam ser organizados, executados e avaliados de forma equivalente. A linguagem escolhida não altera os objetivos, os critérios de avaliação, os testes nem o rigor da correção.

# 1. Linguagens permitidas

Você poderá desenvolver os laboratórios em:

- C++;
- Java;
- Python.

# 2. Regra principal da M1

Na M1, várias operações deverão ser implementadas manualmente.

Quando o enunciado exigir implementação manual, não será permitido substituir a operação por uma função pronta equivalente da biblioteca.

Bibliotecas poderão ser utilizadas como infraestrutura para:

- abrir e salvar imagens;
- criar matrizes;
- acessar pixels;
- consultar dimensões, canais e tipos;
- interpretar argumentos de linha de comando;
- executar testes.

> Se uma função pronta executa diretamente a operação que está sendo avaliada, ela não pode substituir sua implementação.

# 3. Ambientes suportados

## Windows

O ambiente de referência será **MSYS2 — terminal UCRT64**.

Ele será utilizado nos exemplos de:

- Git;
- compilação;
- CMake;
- Ninja;
- execução em terminal.

## Sistemas Unix-like

Também poderão ser utilizados:

- Linux;
- macOS;
- outros ambientes compatíveis.

O projeto deverá ser portátil e não depender de uma IDE específica.

# 4. Regras de portabilidade

Seu projeto não deverá depender de:

- caminhos absolutos;
- pastas particulares do seu computador;
- letras de unidade como `C:\`;
- arquivos externos ao projeto;
- cliques em interface gráfica;
- alteração manual do código para mudar a entrada;
- variáveis de ambiente não documentadas;
- Google Drive;
- notebook como única forma de execução.

Use caminhos relativos ou argumentos de linha de comando.

# 5. Estrutura comum da entrega

```text
lab_m1_x_nome_sobrenome/
├── README.md
├── REPORT.md
├── AI_USAGE.md
├── lab.json
├── images/
│   ├── input/
│   └── output/
├── results/
├── src/
├── tests/
└── arquivos específicos da linguagem
```

# 6. Arquivos obrigatórios

## `README.md`

Deve explicar:

- qual laboratório está sendo entregue;
- linguagem utilizada;
- dependências;
- como preparar o ambiente;
- como compilar ou instalar;
- como executar;
- exemplos de comandos.

## `REPORT.md`

Mini relatório técnico contendo:

- objetivo;
- operações implementadas;
- testes;
- resultados;
- análise técnica;
- limitações.

## `AI_USAGE.md`

Declaração de uso ou não uso de Inteligência Artificial generativa.

## `lab.json`

Exemplo:

```json
{
  "schema_version": 1,
  "lab": "m1.1",
  "language": "cpp",
  "student": { "name": "Nome Sobrenome" }
}
```

Valores previstos para `language`:

```text
cpp
java
python
```

Valores previstos para `lab`:

```text
m1.1
m1.2
m1.3
```

# 7. Execução por linha de comando

Todos os projetos deverão disponibilizar uma aplicação executável por linha de comando.

Forma geral:

```bash
pdi_lab \
  --input <arquivo> \
  --output <arquivo-ou-diretorio> \
  --operation <operacao> \
  [opcoes]
```

A aplicação não poderá exigir interface gráfica para executar as operações avaliadas.

# 8. Argumentos comuns

## `--input`

Imagem de entrada.

```bash
--input images/input/test.png
```

## `--output`

Arquivo ou diretório de saída.

```bash
--output images/output/result.png
```

## `--operation`

Operação solicitada.

```bash
--operation grayscale_weighted
```

## Parâmetros adicionais

Algumas operações poderão usar:

```text
--value
--levels
--threshold
--alpha
--kernel
--border
```

# 9. Operações padronizadas

## M1.1

```text
inspect
copy
channel_b
channel_g
channel_r
grayscale_average
grayscale_weighted
quantize
```

## M1.2

```text
brightness
contrast
negative
threshold
histogram
```

## M1.3

```text
convolution
mean_filter
weighted_mean
laplacian
sobel
```

# 10. Exemplos de execução

## Níveis de cinza

```bash
pdi_lab \
  --input images/input/test.png \
  --output images/output/gray.png \
  --operation grayscale_weighted
```

## Quantização

```bash
pdi_lab \
  --input images/input/test.png \
  --output images/output/quant_8.png \
  --operation quantize \
  --levels 8
```

## Brilho

```bash
pdi_lab \
  --input images/input/test.png \
  --output images/output/brightness.png \
  --operation brightness \
  --value 30
```

## Contraste

```bash
pdi_lab \
  --input images/input/test.png \
  --output images/output/contrast.png \
  --operation contrast \
  --alpha 1.5
```

## Limiarização

```bash
pdi_lab \
  --input images/input/test.png \
  --output images/output/threshold.png \
  --operation threshold \
  --threshold 128
```

## Convolução

```bash
pdi_lab \
  --input images/input/test.png \
  --output images/output/convolution.png \
  --operation convolution \
  --kernel kernels/identity_3x3.txt \
  --border replicate
```

# 11. Formato dos kernels

Exemplo de kernel identidade `3 × 3`:

```text
3 3
0 0 0
0 1 0
0 0 0
```

A primeira linha informa o número de linhas e colunas. As linhas seguintes contêm os valores.

Seu programa deverá validar, quando aplicável:

- existência do arquivo;
- quantidade correta de valores;
- kernel quadrado;
- dimensão ímpar.

# 12. Estratégias de borda

No M1.3 serão utilizados inicialmente:

```text
copy
replicate
```

## `copy`

Pixels em que a vizinhança não cabe integralmente mantêm o valor correspondente da entrada.

## `replicate`

Uma coordenada fora da imagem é substituída pela coordenada válida mais próxima.

# 13. Saídas

## Operações que produzem imagens

O arquivo deverá ser criado exatamente no caminho indicado por `--output`.

A avaliação poderá verificar:

- existência do arquivo;
- largura;
- altura;
- canais;
- valores de pixels;
- saturação;
- comportamento nas bordas.

## `inspect`

Exemplo de saída:

```text
width=640
height=480
channels=3
pixels=307200
type=...
```

## `histogram`

Formato CSV:

```text
intensity,count
0,12
1,7
2,19
...
255,3
```

Para imagens de 8 bits, devem existir 256 linhas de dados, além do cabeçalho.

# 14. Mensagens e códigos de saída

Em caso de sucesso, a aplicação deve retornar:

```text
0
```

Em caso de erro:

```text
valor diferente de 0
```

Erros devem ser informados de forma clara.

# 15. Guardas esperadas

Dependendo da operação, seu programa deverá tratar:

- arquivo inexistente;
- falha ao abrir imagem;
- quantidade inesperada de canais;
- nível de quantização inválido;
- limiar inválido;
- `alpha` inválido;
- kernel inexistente;
- kernel vazio;
- kernel não quadrado;
- kernel de dimensão par;
- estratégia de borda inválida;
- valores fora do intervalo permitido;
- saturação;
- conversões numéricas.

# 16. Determinismo e reprodutibilidade

Executar novamente a mesma operação com a mesma entrada, os mesmos parâmetros e o mesmo código deve produzir o mesmo resultado.

As operações da M1 não devem depender de:

- números aleatórios;
- horário;
- entrada interativa;
- estado externo não documentado.

# 17. Testes

Você receberá imagens e casos públicos para desenvolvimento e validação.

A avaliação também poderá utilizar casos adicionais compatíveis com o enunciado, como:

- imagem `1 × 1`;
- imagem `2 × 2`;
- imagem constante;
- impulso;
- degrau vertical;
- degrau horizontal;
- valores `0` e `255`;
- formas geométricas simples;
- conteúdo tocando as bordas.

Esses casos não introduzirão requisitos novos.

# 18. Cuidados numéricos

Use tipos adequados durante os cálculos.

Evite:

- overflow;
- saturação prematura;
- conversões prematuras;
- perda desnecessária de precisão.

Isso é especialmente importante em:

- níveis de cinza ponderado;
- contraste;
- convolução;
- Laplaciano;
- Sobel;
- magnitude de gradiente.

# 19. Projeto-base C++

Estrutura esperada:

```text
lab_m1_x/
├── CMakeLists.txt
├── CMakePresets.json
├── README.md
├── REPORT.md
├── AI_USAGE.md
├── lab.json
├── include/
├── src/
├── tests/
├── kernels/
├── images/
├── results/
└── build/        # não versionado
```

No Windows/MSYS2 UCRT64:

```bash
cmake --preset ucrt64-debug
cmake --build --preset ucrt64-debug
./build/ucrt64-debug/pdi_lab.exe --help
```

Em Unix-like:

```bash
cmake -S . -B build/unix-debug -G Ninja -DCMAKE_BUILD_TYPE=Debug
cmake --build build/unix-debug
./build/unix-debug/pdi_lab --help
```

# 20. Projeto-base Java

Estrutura esperada:

```text
lab_m1_x/
├── pom.xml
├── README.md
├── REPORT.md
├── AI_USAGE.md
├── lab.json
├── src/
│   ├── main/java/
│   └── test/java/
├── kernels/
├── images/
├── results/
└── target/       # não versionado
```

Construção e testes:

```bash
mvn test
mvn package
```

Execução:

```bash
java -jar target/pdi-lab.jar --help
```

# 21. Projeto-base Python

Estrutura esperada:

```text
lab_m1_x/
├── requirements.txt
├── README.md
├── REPORT.md
├── AI_USAGE.md
├── lab.json
├── src/
│   └── pdi_lab/
├── tests/
├── kernels/
├── images/
├── results/
└── .venv/        # não versionado
```

Preparação:

```bash
python -m venv .venv
python -m pip install -r requirements.txt
```

Testes:

```bash
python -m pytest
```

Execução:

```bash
python -m pdi_lab --help
```

Notebooks podem ser utilizados como material complementar, mas não como única forma de execução.

# 22. Arquivos que não devem ser entregues

Não inclua:

```text
build/
target/
.venv/
__pycache__/
.pytest_cache/
.idea/
```

Evite também executáveis gerados, caches, arquivos temporários e bibliotecas duplicadas.

# 23. Checklist antes da entrega

- [ ] uso somente caminhos relativos ou argumentos;
- [ ] outra pessoa consegue seguir meu `README.md`;
- [ ] consigo reconstruir o projeto do zero;
- [ ] os testes executam;
- [ ] a aplicação funciona pela linha de comando;
- [ ] as saídas são geradas no local solicitado;
- [ ] entradas inválidas são tratadas;
- [ ] operações manuais não foram substituídas por funções prontas;
- [ ] `REPORT.md` está preenchido;
- [ ] `AI_USAGE.md` está preenchido;
- [ ] `lab.json` está válido;
- [ ] não entreguei arquivos de build, cache ou ambiente virtual.

# 24. Relação com a avaliação

| Critério | Evidências |
|---|---|
| Execução | compilação, execução, códigos de saída e arquivos gerados |
| Aquisição e requisitos | argumentos, parâmetros, estrutura e formatos |
| Corretude | resultados, pixels, histogramas e cálculos |
| Guardas | entradas inválidas, limites, saturação, kernels e bordas |
| Análise | testes, relatório e interpretação dos resultados |

A correção automatizada será apenas uma parte da avaliação. Também haverá inspeção do código, do relatório, das decisões tomadas e da coerência entre implementação e resultados.

# 25. Projeto-base não é solução pronta

Os projetos-base fornecidos pela disciplina poderão incluir:

- estrutura de diretórios;
- configuração da linguagem;
- dependências;
- leitura de argumentos;
- função principal;
- exemplo simples de leitura e escrita;
- estrutura inicial de testes.

Eles não fornecerão a solução das operações avaliadas.

# 26. Objetivo da padronização

A padronização não existe para obrigar todos os projetos a terem a mesma implementação.

Ela permite que projetos em linguagens diferentes possam ser avaliados de forma comparável:

```text
seu algoritmo
    ↓
interface padronizada
    ↓
testes e avaliação
```

O que será avaliado continua sendo sua capacidade de implementar, testar, tratar casos especiais, explicar e analisar os resultados.