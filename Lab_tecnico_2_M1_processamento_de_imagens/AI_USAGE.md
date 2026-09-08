# Declaração de uso de Inteligência Artificial generativa

Declaro que utilizei ferramenta de Inteligência Artificial generativa na
elaboração deste laboratório, conforme detalhado abaixo.

## Ferramenta utilizada

Claude, da Anthropic, executado pela interface Claude Code, modelo Opus.

## Finalidade

1. auditoria do código que eu já havia escrito, comparando a implementação com
   o enunciado, com o contrato técnico e com a rubrica, para identificar
   requisitos não atendidos;
2. reorganização do projeto na estrutura exigida pela disciplina, com pacote em
   `src/pdi_lab` e interface de linha de comando padronizada;
3. redação da documentação de entrega, criação da suíte de testes e apuração
   das estatísticas usadas na análise do relatório.

## Partes afetadas

Escritas ou reescritas com auxílio da ferramenta:

- `src/pdi_lab/cli.py`, `src/pdi_lab/image_io.py`, `src/pdi_lab/errors.py`,
  `src/pdi_lab/__init__.py`, `src/pdi_lab/__main__.py`;
- reorganização de `src/pdi_lab/operations.py`, partindo das funções que eu já
  havia implementado em `lab_2_m1.py`;
- `tests/test_operations.py`, `tests/test_cli.py`, `tests/test_structure.py`,
  `conftest.py`;
- `README.md`, `REPORT.md`, este arquivo, `pyproject.toml`, `.gitignore` e o
  script de reprodução `lab_2_m1.py`.

Trabalho meu, anterior ao uso da ferramenta:

- a lógica das cinco transformações do laboratório, incluindo o percurso dos
  pixels, as fórmulas de brilho, contraste, negativo e limiarização, e a
  contagem manual do histograma em 256 posições;
- o diagnóstico e a correção do estouro em `uint8` no ajuste de brilho, que
  resolvi durante o desenvolvimento e relatei em `mural.md`;
- a escolha e a preparação da imagem de teste.

## O que a auditoria apontou

A lógica das transformações estava correta e foi mantida. Os pontos corrigidos
foram de formato, guardas e interface:

- o histograma era gravado como `.txt`, com nome contendo espaços, cabeçalho
  `intensidade,quantidade` e separador com espaço depois da vírgula. O contrato
  define CSV com cabeçalho `intensity,count`;
- `cv.imread` devolvendo `None` não era tratado, e o programa quebrava com
  `AttributeError` em vez de mensagem clara;
- não havia validação de `alpha`, e o deslocamento de brilho estava fixo em 50
  dentro do código;
- não havia interface de linha de comando nem códigos de saída;
- as imagens da limiarização não constavam entre as saídas geradas;
- havia código morto no `main`, uma matriz 4 por 4 criada e nunca usada.

## Forma de validação

- Executei `python -m pytest` e confirmei os 60 testes aprovados.
- Conferi à mão os valores esperados nos testes de imagem sintética 2 por 2,
  refazendo as contas das quatro transformações, inclusive os casos de
  saturação.
- Executei cada operação pela linha de comando e verifiquei os arquivos
  gerados e os códigos de saída 0, 1 e 2.
- Verifiquei as identidades do histograma diretamente nos arquivos CSV: soma
  igual ao total de pixels, histograma do negativo como espelho do original,
  contagem saturada após o brilho igual à soma da cauda do histograma original,
  e contagem abaixo do limiar igual à soma correspondente na origem.
- Criei uma rampa sintética com histograma uniforme e conferi na mão as
  previsões de saturação, incluindo o valor 2752 igual a 43 vezes 64 em cada
  extremo do contraste 1,5.
- Reli o código gerado, linha a linha, antes de aceitá-lo, e sou responsável
  pelo conteúdo entregue.

## Modificações realizadas por mim

Revisei nomes, comentários e mensagens de erro para manter a convenção do
projeto, com texto em português e identificadores em inglês, e mantive a lógica
original das transformações em vez de aceitar reescritas vetorizadas, que
violariam a exigência de implementação manual do enunciado.

## Registro

Registro equivalente: o histórico de commits deste repositório separa o estado
anterior ao uso da ferramenta, no commit `6da0b28`, do estado posterior à
revisão, permitindo comparar o que foi alterado e por quê. As justificativas
técnicas de cada decisão estão na seção 4 do `REPORT.md`.
