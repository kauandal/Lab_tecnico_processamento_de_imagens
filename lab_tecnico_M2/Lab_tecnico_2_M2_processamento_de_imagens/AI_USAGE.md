# Declaração de uso de Inteligência Artificial generativa

Declaro que utilizei ferramenta de Inteligência Artificial generativa na
elaboração dos laboratórios M2.1 e M2.2, conforme detalhado abaixo.

## Ferramenta utilizada

Claude, da Anthropic, executado pela interface Claude Code, modelo Opus.

## Finalidade

Quatro finalidades, em ordem de importância:

1. implementação da operação `segment` do M2.1, partindo da estrutura do
   projeto da M1, com os métodos `fixed`, `otsu`, `adaptive` e `hsv`, a
   validação da máscara e a sobreposição;
2. implementação da operação `analyze` do M2.2, com rotulação em
   conectividade 4 e 8, sequência morfológica lida de arquivo, filtro por área,
   CSV, imagem de rótulos e resumo;
3. busca de uma imagem pública de moedas com licença verificada, que resultou
   em `coins.png`, e montagem dos scripts que reproduzem os estudos;
4. redação da documentação de entrega e da suíte de testes.

## Partes afetadas

Escritas ou reescritas com auxílio da ferramenta:

- `src/pdi_lab/cli.py`, `src/pdi_lab/segmentation.py`,
  `src/pdi_lab/analysis.py`, `src/pdi_lab/image_io.py`,
  `src/pdi_lab/__init__.py`;
- `lab_1_m2.py`, `lab_2_m2.py`, `config/sequence.json`,
  `config/sequence_close15.json`;
- `tests/test_segmentation.py`, `tests/test_cli.py`,
  `tests/test_real_images.py`, `tests/test_analysis.py`,
  `tests/test_real_analysis.py`, `tests/test_structure.py`;
- `README.md`, `REPORT.md`, `pyproject.toml`, `lab.json`

Aproveitados da M1 sem mudança: `src/pdi_lab/errors.py`,
`src/pdi_lab/__main__.py`, `conftest.py` e `.gitignore`.

Trabalho meu, anterior ao uso da ferramenta:

- a escolha do alvo, moedas;
- a escolha da imagem em condição favorável, `moedas_brasileiras.jpg`.

## Correções apontadas pela ferramenta

- Uma primeira imagem de teste, `aura.jpg`, tinha marca d'água de banco de
  imagens. Ela foi retirada do projeto, porque o enunciado exige imagem com
  permissão de uso.
- No método `adaptive`, um valor padrão para `C` esconderia que regiões
  planas viram objeto quando `C` é positivo. Por isso `--c` passou a ser
  obrigatório.
- O log de execução e os arquivos de resultado gravavam caminhos absolutos do
  computador. Passaram a usar caminhos relativos à raiz do projeto.
- No M2.2, a contagem após a abertura subiu em vez de cair. A conferência
  mostrou que a abertura partiu duas moedas da linha de baixo de `coins.png`
  em cinco pedaços, que o fechamento juntou de novo. Isso está registrado na
  seção 9.5 do `REPORT.md`.

## Forma de validação

- Execução de `python -m pytest`, com os 107 testes aprovados.
- Execução de `python lab_1_m2.py` e `python lab_2_m2.py` e conferência
  visual das figuras de comparação, dos estágios e das imagens de rótulos.
- Execução de cada operação pela linha de comando, verificando os códigos de
  saída 0, 1 e 2.
- Conferência do hash SHA-256 de `coins.png` com o registro do scikit-image.

Pendente: descrever aqui a revisão feita por mim no código e no relatório
antes da entrega.

## Modificações realizadas por mim

Pendente.

## Registro

As justificativas técnicas de cada decisão estão nas seções 4 e 9.3 do
`REPORT.md`, e a saída completa da execução está em `results/execucao.log`.
