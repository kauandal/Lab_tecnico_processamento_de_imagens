# Declaração de uso de Inteligência Artificial generativa

Declaro que utilizei ferramenta de Inteligência Artificial generativa na
elaboração deste laboratório, conforme detalhado abaixo.

## Ferramenta utilizada

Claude, da Anthropic, executado pela interface Claude Code, modelo Opus.

## Finalidade

Três finalidades, em ordem de importância:

1. implementação da operação `segment`, partindo da estrutura do projeto da
   M1, com os métodos `fixed`, `otsu`, `adaptive` e `hsv`, a validação da
   máscara e a sobreposição;
2. busca de imagens públicas de moedas com licença verificada, que resultou
   em `coins.png` e `moedas_real_separadas.jpg`, e montagem do script que
   reproduz o estudo;
3. redação da documentação de entrega e da suíte de testes.

## Partes afetadas

Escritas ou reescritas com auxílio da ferramenta:

- `src/pdi_lab/cli.py`, `src/pdi_lab/segmentation.py`,
  `src/pdi_lab/image_io.py`, `src/pdi_lab/__init__.py`;
- `lab_1_m2.py`;
- `tests/test_segmentation.py`, `tests/test_cli.py`,
  `tests/test_real_images.py`, `tests/test_structure.py`;
- `README.md`, `REPORT.md`, `pyproject.toml`, `lab.json`

Aproveitados da M1 sem mudança: `src/pdi_lab/errors.py`,
`src/pdi_lab/__main__.py`, `conftest.py` e `.gitignore`.

Trabalho meu, anterior ao uso da ferramenta:

- a escolha do alvo, moedas;
- a decisão de trocar a imagem em condição favorável por uma com licença
  verificável.

## Correções apontadas pela ferramenta

- Uma primeira imagem de teste, `aura.jpg`, tinha marca d'água de banco de
  imagens. Ela foi retirada do projeto, porque o enunciado exige imagem com
  permissão de uso.
- A imagem favorável da primeira versão, `moedas_brasileiras.jpg`, não tinha
  fonte nem licença conhecidas. Ela foi trocada por `moedas_real_separadas.jpg`,
  do Wikimedia Commons, sob CC BY-SA 2.5, e o estudo foi refeito.
- As sobreposições das fotos em PNG tinham 13 MB cada. Passaram a ser gravadas
  em JPEG, já que só a máscara precisa ser sem perdas.
- No método `adaptive`, um valor padrão para `C` esconderia que regiões
  planas viram objeto quando `C` é positivo. Por isso `--c` passou a ser
  obrigatório.
- O log de execução e os arquivos de resultado gravavam caminhos absolutos do
  computador. Passaram a usar caminhos relativos à raiz do projeto.

## Forma de validação

- Execução de `python -m pytest`, com os 70 testes aprovados.
- Execução de `python lab_1_m2.py` e conferência visual das figuras de
  comparação e das sobreposições.
- Execução de cada método pela linha de comando, verificando os códigos de
  saída 0, 1 e 2.
- Conferência do hash SHA-256 de `coins.png` com o registro do scikit-image
  e da licença de `moedas_real_separadas.jpg` na página do arquivo no
  Wikimedia Commons.

Pendente: descrever aqui a revisão feita por mim no código e no relatório
antes da entrega.

## Modificações realizadas por mim

Pendente.

## Registro

As justificativas técnicas de cada decisão estão na seção 4 do `REPORT.md`, e
a saída completa da execução está em `results/execucao.log`.
