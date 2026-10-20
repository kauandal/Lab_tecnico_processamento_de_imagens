# Declaração de uso de Inteligência Artificial generativa

Declaro que utilizei ferramenta de Inteligência Artificial generativa na
elaboração dos laboratórios M2.1 e M2.2, conforme detalhado abaixo.

## Ferramenta utilizada

Claude, da Anthropic, executado pela interface Claude Code, modelo Opus.

## Finalidade

Cinco finalidades, em ordem de importância:

1. implementação da operação `segment` do M2.1, escrita do zero com a
   ferramenta a partir da estrutura dos meus projetos da M1, com os métodos
   `fixed`, `otsu`, `adaptive` e `hsv`, a validação da máscara e a
   sobreposição;
2. implementação da operação `analyze` do M2.2, com rotulação em
   conectividade 4 e 8, sequência morfológica lida de arquivo, filtro por área,
   CSV, imagem de rótulos e resumo;
3. busca de imagens públicas de moedas com licença verificada, que resultou
   em `coins.png` e nas duas fotos de moedas do real do Wikimedia Commons;
4. montagem dos scripts `lab_1_m2.py` e `lab_2_m2.py`, que reproduzem os
   estudos, e escolha dos parâmetros a partir das medidas feitas nas imagens;
5. redação da documentação de entrega e da suíte de testes.

## Partes afetadas

Escritas com auxílio da ferramenta:

- `src/pdi_lab/cli.py`, `src/pdi_lab/segmentation.py`,
  `src/pdi_lab/analysis.py`, `src/pdi_lab/image_io.py`,
  `src/pdi_lab/__init__.py`;
- `lab_1_m2.py`, `lab_2_m2.py`, `config/coins.json`,
  `config/moedas_real.json`;
- `tests/test_segmentation.py`, `tests/test_cli.py`,
  `tests/test_real_images.py`, `tests/test_analysis.py`,
  `tests/test_real_analysis.py`, `tests/test_structure.py`;
- `README.md`, `REPORT.md`, `AI_USAGE.md`, `pyproject.toml`, `lab.json`.

Copiados dos meus projetos da M1 sem mudança: `src/pdi_lab/errors.py`,
`src/pdi_lab/__main__.py`, `conftest.py` e `.gitignore`.

Não havia código da M2 antes do uso da ferramenta. As pastas dos dois
laboratórios tinham só os enunciados. O projeto do M2.2 começou como cópia do
projeto do M2.1.

Decisões tomadas por mim durante o trabalho:

- o alvo, moedas, escolhido entre as opções de imagem sugeridas;
- manter uma pasta por laboratório, como na M1, copiando o projeto do M2.1
  para o M2.2;
- seguir o padrão de escrita, a ordem das seções e o nível de detalhe dos
  meus relatórios da M1;
- trocar a imagem em condição favorável por uma com licença verificável e
  incluir uma terceira imagem, com moedas encostadas, para o caso de contato.

## Correções apontadas pela ferramenta

- Uma primeira imagem de teste, `aura.jpg`, tinha marca d'água de banco de
  imagens. Ela foi retirada do projeto, porque o enunciado exige imagem com
  permissão de uso.
- A imagem favorável da primeira versão, `moedas_brasileiras.jpg`, não tinha
  fonte nem licença conhecidas. Ela foi trocada por `moedas_real_separadas.jpg`,
  do Wikimedia Commons, sob CC BY-SA 2.5, e os estudos foram refeitos.
- As sobreposições das fotos em PNG tinham 13 MB cada. Passaram a ser gravadas
  em JPEG, já que só a máscara precisa ser sem perdas.
- No método `adaptive`, um valor padrão para `C` esconderia que regiões
  planas viram objeto quando `C` é positivo. Por isso `--c` passou a ser
  obrigatório.
- O log de execução e os arquivos de resultado gravavam caminhos absolutos do
  computador. Passaram a usar caminhos relativos à raiz do projeto.
- No M2.2, a contagem filtrada de `moedas_real_separadas.jpg` caiu de 12 para
  11 depois da abertura. A conferência mostrou que a moeda prateada de 50
  centavos se partiu em 131 pedaços, que o fechamento juntou de novo. Isso
  está registrado na seção 9.5 do `REPORT.md`.
- Uma frase do relatório dizia que as moedas separadas ficavam a mais de 100
  pixels umas das outras. A medida mostrou 68 pixels, e o texto foi
  corrigido.

## Forma de validação

- Execução de `python -m pytest`, com os 111 testes aprovados.
- Execução de `python lab_1_m2.py` e `python lab_2_m2.py` e conferência
  visual das figuras de comparação, dos estágios e das imagens de rótulos.
- Execução de cada operação pela linha de comando, verificando os códigos de
  saída 0, 1 e 2.
- Conferência do hash SHA-256 de `coins.png` com o registro do scikit-image
  e da licença das duas fotos na página de cada arquivo no Wikimedia
  Commons.
- Revisão manual, feita por mim, do código gerado e do relatório.

## Modificações realizadas

Não fiz alterações diretas no código gerado. As mudanças em relação à
primeira versão foram pedidas por mim e executadas com a ferramenta:

- reescrita do `README.md`, do `REPORT.md` e deste arquivo para seguir o
  padrão dos meus laboratórios da M1, com texto mais simples;
- retirada da opção `--summary` da operação `segment`, que gravava um JSON
  por execução, para deixar a interface mais simples;
- troca dos scripts dos estudos por `lab_1_m2.py` e `lab_2_m2.py`, no mesmo
  formato dos scripts da M1;
- troca da imagem em condição favorável e inclusão da foto das moedas
  empilhadas, descritas na seção anterior. Com a foto empilhada mostrando a
  fusão de moedas, o caso de comparação com fechamento 15 x 15 em `coins.png`
  foi retirado.

## Registro

Não há link compartilhável da conversa. O registro equivalente é o histórico
de commits deste repositório: o código do M2.1 entrou no commit `9f80f8a`, o
do M2.2 no commit `a7a41f6` e a troca de imagens no commit `bfc4ed2`, todos
com conteúdo gerado com a ferramenta e revisado por mim. As justificativas
técnicas de cada decisão estão nas seções 4 e 9.3 do `REPORT.md`, e a saída
completa da execução está em `results/execucao.log`.
