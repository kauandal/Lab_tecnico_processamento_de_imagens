# Declaração de uso de Inteligência Artificial generativa

Declaro que utilizei ferramenta de Inteligência Artificial generativa na
elaboração deste laboratório, conforme detalhado abaixo.

## Ferramenta utilizada

Claude, da Anthropic, executado pela interface Claude Code, modelo Opus.

## Finalidade

1. completar a implementação, que estava parcial, com as operações que faltavam;
2. organizar o projeto na estrutura exigida pela disciplina, com pacote em
   `src/pdi_lab` e interface de linha de comando padronizada;
3. criar a suíte de testes e a documentação de entrega, além de apurar as
   estatísticas usadas na análise do relatório.

## Estado anterior ao uso da ferramenta

O que eu já havia implementado em `lab_3_m1.py`:

- conversão manual para níveis de cinza;
- função genérica de convolução com percurso explícito da vizinhança, incluindo
  o cálculo do raio a partir do tamanho do kernel;
- validação de kernel quadrado e de dimensão ímpar;
- kernels de identidade, média 3 por 3, média 5 por 5 e Laplaciano;
- geração de imagem sintética em padrão xadrez;
- geração das saídas de convolução.

O que faltava, conforme o enunciado:

- as duas estratégias de borda. A versão anterior deixava a moldura zerada, o
  que não é `copy`, que preserva o valor original, nem `replicate`, que repete o
  pixel mais próximo;
- preservação da resposta bruta. O `clip` estava dentro do laço, o que saturava
  antes da hora e inviabilizava o Laplaciano, cuja resposta é negativa em 47%
  dos pixels desta imagem;
- média ponderada 3 por 3;
- aplicação do Laplaciano e a imagem realçada;
- Sobel completo, com `Gx`, `Gy`, `|Gx| + |Gy|` e `sqrt(Gx² + Gy²)`;
- leitura dos kernels a partir dos arquivos em `kernels/`, que existiam mas não
  eram usados;
- interface de linha de comando e códigos de saída;
- testes automatizados.

## Partes afetadas

Escritas ou reescritas com auxílio da ferramenta:

- `src/pdi_lab/operations.py`, partindo da minha função de convolução, com a
  correção do momento da saturação e a adição das estratégias de borda,
  Laplaciano, realce, Sobel e modos de visualização;
- `src/pdi_lab/kernels.py`, `src/pdi_lab/cli.py`, `src/pdi_lab/image_io.py`,
  `src/pdi_lab/errors.py`, `src/pdi_lab/__init__.py`, `src/pdi_lab/__main__.py`;
- `tests/test_operations.py`, `tests/test_kernels.py`, `tests/test_cli.py`,
  `tests/test_structure.py`, `conftest.py`;
- os kernels adicionados em `kernels/`;
- `README.md`, `REPORT.md`, este arquivo, `pyproject.toml`, `.gitignore` e o
  script de reprodução `lab_3_m1.py`.

## Forma de validação

- Executei `python -m pytest` e confirmei os 92 testes aprovados.
- Conferi à mão os valores dos casos sintéticos, refazendo as contas do
  material: vizinhos 100 com centro 150 dão `-200`, com centro 50 dão `+200`, a
  vizinhança `[[0,0,255],[0,0,255],[0,0,255]]` dá `Gx = 1020`, e o impulso com
  média 3 por 3 espalha `255/9`, igual a 28,3333, em nove posições.
- Verifiquei que o kernel identidade reproduz a imagem nas duas estratégias de
  borda.
- Verifiquei nos degraus sintéticos que `Gy` é identicamente zero no degrau
  vertical e `Gx` é identicamente zero no horizontal, conferindo os arquivos
  brutos em `results/`.
- Verifiquei que a diferença entre `copy` e `replicate` é exatamente zero a
  partir da distância igual ao raio do kernel, com os perfis em
  `results/border_profile_mean_3.csv` e `border_profile_mean_5.csv`. O material
  avisa que, se a imagem inteira mudar, há erro de índices.
- Confirmei que a resposta do Laplaciano soma exatamente zero na imagem, o que
  decorre da soma dos coeficientes do kernel ser zero.
- Confirmei que o realce com fator 1 produz o mesmo resultado que a convolução
  direta com o kernel de afiamento.
- Reli o código gerado, linha a linha, antes de aceitá-lo, e sou responsável
  pelo conteúdo entregue.

## Modificações realizadas por mim

Revisei nomes, comentários e mensagens de erro para manter a convenção do
projeto, com texto em português e identificadores em inglês. Mantive o percurso
explícito das vizinhanças em vez de aceitar qualquer reescrita vetorizada, que
violaria a exigência de implementação manual do enunciado, e mantive a convenção
de correlação adotada pelo material da disciplina, em vez da convolução
matemática estrita.

## Registro

Registro equivalente: o histórico de commits deste repositório separa o estado
anterior ao uso da ferramenta, com a implementação parcial, do estado posterior.
As justificativas técnicas de cada decisão estão na seção 4 do `REPORT.md`, e as
limitações assumidas na seção 8.
