# Limitação de coordenadas na estratégia de borda replicate

## 1. Expressão utilizada

Na estratégia de borda **replicate**, as coordenadas que ultrapassam a imagem são substituídas pelas coordenadas válidas mais próximas:

$$
x' = \min\bigl(\max(x,0),W-1\bigr)
$$

$$
y' = \min\bigl(\max(y,0),H-1\bigr)
$$

## 2. Significado dos símbolos

- $x$: coordenada horizontal que se deseja acessar;
- $y$: coordenada vertical que se deseja acessar;
- $W$: largura da imagem, isto é, o número de colunas;
- $H$: altura da imagem, isto é, o número de linhas;
- $x'$: coordenada horizontal corrigida;
- $y'$: coordenada vertical corrigida.

Como os índices começam em zero, as coordenadas válidas são:

$$
0 \leq x \leq W-1
$$

$$
0 \leq y \leq H-1
$$

Assim, $W-1$ é o índice da última coluna e $H-1$ é o índice da última linha.

## 3. Como ler a expressão de x

Considere:

$$
x' = \min\bigl(\max(x,0),W-1\bigr)
$$

Primeiro, calcula-se:

$$
\max(x,0)
$$

Essa operação escolhe o maior valor entre $x$ e zero. Portanto, impede que a coordenada fique negativa.

Depois, calcula-se:

$$
\min\bigl(\max(x,0),W-1\bigr)
$$

Essa operação escolhe o menor valor entre o resultado anterior e $W-1$. Portanto, impede que a coordenada ultrapasse a última coluna.

Em palavras:

> A coordenada $x'$ é o valor de $x$ limitado ao intervalo entre $0$ e $W-1$.

## 4. Como ler a expressão de y

O mesmo raciocínio é aplicado a:

$$
y' = \min\bigl(\max(y,0),H-1\bigr)
$$

Em palavras:

> A coordenada $y'$ é o valor de $y$ limitado ao intervalo entre $0$ e $H-1$.

## 5. Exemplo com uma imagem 5 × 4

Considere uma imagem com:

$$
W=5
$$

$$
H=4
$$

Ela possui:

- cinco colunas, numeradas de $0$ a $4$;
- quatro linhas, numeradas de $0$ a $3$.

Portanto:

$$
0 \leq x \leq 4
$$

$$
0 \leq y \leq 3
$$

### Exemplos para x

| Coordenada solicitada | Cálculo | Coordenada corrigida |
|---|---|---|
| $x=-1$ | $\min(\max(-1,0),4)$ | $x'=0$ |
| $x=2$ | $\min(\max(2,0),4)$ | $x'=2$ |
| $x=5$ | $\min(\max(5,0),4)$ | $x'=4$ |

### Exemplos para y

| Coordenada solicitada | Cálculo | Coordenada corrigida |
|---|---|---|
| $y=-1$ | $\min(\max(-1,0),3)$ | $y'=0$ |
| $y=2$ | $\min(\max(2,0),3)$ | $y'=2$ |
| $y=4$ | $\min(\max(4,0),3)$ | $y'=3$ |

## 6. Relação com a estratégia replicate

Considere uma âncora no canto superior esquerdo, em $(0,0)$, e uma posição relativa $(-1,-1)$:

$$
x = 0 + (-1) = -1
$$

$$
y = 0 + (-1) = -1
$$

Aplicando a limitação:

$$
x' = \min\bigl(\max(-1,0),W-1\bigr)=0
$$

$$
y' = \min\bigl(\max(-1,0),H-1\bigr)=0
$$

Assim, o acesso externo $(-1,-1)$ é substituído por $(0,0)$. O pixel do canto é reutilizado.

## 7. Forma equivalente com clamp

Essa operação também pode ser escrita com uma função chamada **clamp** ou **limitar**:

$$
x' = \operatorname{clamp}(x,0,W-1)
$$

$$
y' = \operatorname{clamp}(y,0,H-1)
$$

### Pseudocódigo

    FUNÇÃO limitar(valor, mínimo, máximo):

        SE valor < mínimo:
            RETORNAR mínimo

        SE valor > máximo:
            RETORNAR máximo

        RETORNAR valor

Aplicação na vizinhança:

    imagemX ← limitar(x + Δx, 0, largura - 1)
    imagemY ← limitar(y + Δy, 0, altura - 1)

## 8. Síntese

- $W$ representa a quantidade de colunas;
- $H$ representa a quantidade de linhas;
- $W-1$ é a última coluna válida;
- $H-1$ é a última linha válida;
- valores negativos são substituídos por zero;
- valores maiores que o limite são substituídos pelo último índice válido;
- na estratégia **replicate**, isso reutiliza o pixel mais próximo da borda.
