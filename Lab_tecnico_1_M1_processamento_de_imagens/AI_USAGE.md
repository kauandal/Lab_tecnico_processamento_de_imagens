# Declaração de uso de Inteligência Artificial generativa

Declaro que utilizei ferramenta de Inteligência Artificial generativa na
elaboração deste laboratório, conforme detalhado abaixo.

## Ferramenta utilizada

Claude, da Anthropic, executado pela interface Claude Code, modelo Opus.

## Finalidade

Três finalidades, em ordem de importância:

1. auditoria do código que eu já havia escrito, comparando a implementação com
   o enunciado do laboratório, com o contrato técnico e com a rubrica, para
   identificar requisitos não atendidos;
2. reorganização do projeto na estrutura exigida pela disciplina, com pacote em
   `src/pdi_lab` e interface de linha de comando padronizada;
3. redação da documentação de entrega e ampliação da suíte de testes.

## Partes afetadas

Escritas ou reescritas com auxílio da ferramenta:

- `src/pdi_lab/cli.py`, `src/pdi_lab/image_io.py`, `src/pdi_lab/errors.py`,
  `src/pdi_lab/__init__.py`, `src/pdi_lab/__main__.py`;
- reorganização de `src/pdi_lab/operations.py`, partindo das funções que eu já
  havia implementado em `lab_1_m1.py`;
- `tests/test_operations.py`, `tests/test_cli.py`, `tests/test_structure.py`,
  `conftest.py`;
- `README.md`, `REPORT.md`, este arquivo, `pyproject.toml`, `.gitignore` e o
  script de reprodução `lab_1_m1.py`.

Trabalho meu, anterior ao uso da ferramenta:

- a lógica original de todas as operações do laboratório, incluindo o percurso
  dos pixels, as fórmulas das duas conversões para níveis de cinza e o cálculo
  da quantização por passo;
- a escolha e a preparação das imagens de teste.

## Correções apontadas pela ferramenta

O item mais relevante foi um defeito de corretude que eu não havia percebido:
na média simples, a soma dos três canais `uint8` estourava antes da divisão,
fazendo um pixel branco resultar em 84 em vez de 255. Esse é o mesmo tipo de
problema que eu já havia enfrentado e corrigido no laboratório M1.2, e que
passou despercebido aqui. O diagnóstico, a correção e o teste de regressão
estão descritos na seção 4.1 do `REPORT.md`.

Outros pontos apontados: inspeção sem valor mínimo, máximo e média; contagem de
pixels multiplicando pelo número de canais; imagens em níveis de cinza gravadas
com três canais; ausência de tratamento para arquivo inexistente; ausência de
códigos de saída; ausência da interface de linha de comando exigida.

## Forma de validação

- Executei `python -m pytest` e confirmei os 44 testes aprovados.
- Conferi à mão os valores esperados nos testes de imagem sintética 2 por 2,
  refazendo as contas das duas fórmulas de cinza e da quantização.
- Executei cada operação pela linha de comando e verifiquei os arquivos
  gerados, além dos códigos de saída 0, 1 e 2.
- Verifiquei que `copy.png` é idêntica à entrada e que a soma dos três canais
  isolados reconstrói a imagem original.
- Confirmei o defeito de estouro reproduzindo o cálculo antigo e o novo sobre o
  mesmo pixel, e comparando o máximo do arquivo antes e depois da correção.
- Reli o código gerado, linha a linha, antes de aceitá-lo, e sou responsável
  pelo conteúdo entregue.

## Modificações realizadas por mim

Revisei os nomes, os comentários e as mensagens de erro para manter a
convenção do projeto, com texto em português e identificadores em inglês, e
mantive a lógica original das operações em vez de aceitar reescritas
vetorizadas, que violariam a exigência de implementação manual do enunciado.

## Registro

Link da conversa: [preencher antes da entrega]

Registro equivalente disponível: o histórico de commits deste repositório
separa o estado anterior ao uso da ferramenta, no commit que entregou a versão
inicial do laboratório, do estado posterior à revisão, permitindo comparar o
que foi alterado e por quê. As justificativas técnicas de cada decisão estão na
seção 4 do `REPORT.md`.
