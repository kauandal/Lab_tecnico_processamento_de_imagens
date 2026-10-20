# Filtro Laplaciano — explicação detalhada

## 1. Ideia central

O filtro Laplaciano mede quanto a intensidade de um pixel difere das intensidades ao seu redor. Ele responde pouco em regiões uniformes e fortemente onde existem mudanças rápidas, como contornos, detalhes finos e ruído.

## 2. Derivada de segunda ordem

Em uma dimensão, a segunda derivada pode ser aproximada por:

$$
f''(x) \approx f(x-1)-2f(x)+f(x+1)
$$

Em uma imagem, calculamos a segunda derivada nas direções $x$ e $y$:

$$
\nabla^2 f=
\frac{\partial^2 f}{\partial x^2}
+
\frac{\partial^2 f}{\partial y^2}
$$

Uma aproximação discreta é:

$$
\nabla^2 f(x,y)
=
f(x-1,y)+f(x+1,y)+f(x,y-1)+f(x,y+1)-4f(x,y)
$$

Isso corresponde ao kernel:

$$
K_L=
\begin{bmatrix}
0&1&0\\
1&-4&1\\
0&1&0
\end{bmatrix}
$$

Ele utiliza o pixel central e seus quatro vizinhos ortogonais.

## 3. Interpretação dos coeficientes

O cálculo é:

$$
L(x,y)=
f(x-1,y)+f(x+1,y)+f(x,y-1)+f(x,y+1)-4f(x,y)
$$

Podemos reescrever:

$$
L(x,y)=4
\left(
\frac{
f(x-1,y)+f(x+1,y)+f(x,y-1)+f(x,y+1)
}{4}
-f(x,y)
\right)
$$

Portanto, o Laplaciano compara:

- a média dos quatro vizinhos;
- o valor do pixel central.

Se o centro for semelhante aos vizinhos, o resultado ficará próximo de zero. Se for muito diferente, a resposta terá grande magnitude.

## 4. Região constante

Considere:

$$
\begin{bmatrix}
100&100&100\\
100&100&100\\
100&100&100
\end{bmatrix}
$$

O cálculo é:

$$
L=100+100+100+100-4(100)
$$

$$
L=400-400=0
$$

Isso acontece porque a soma dos coeficientes do kernel é zero:

$$
0+1+0+1-4+1+0+1+0=0
$$

Logo, o Laplaciano anula regiões constantes.

## 5. Centro mais claro que os vizinhos

Considere:

$$
\begin{bmatrix}
100&100&100\\
100&150&100\\
100&100&100
\end{bmatrix}
$$

Com o kernel de centro $-4$:

$$
L=100+100+100+100-4(150)
$$

$$
L=400-600=-200
$$

A resposta é negativa porque o centro é mais claro que os vizinhos.

## 6. Centro mais escuro que os vizinhos

Agora considere:

$$
\begin{bmatrix}
100&100&100\\
100&50&100\\
100&100&100
\end{bmatrix}
$$

Temos:

$$
L=100+100+100+100-4(50)
$$

$$
L=400-200=200
$$

A resposta é positiva porque o centro é mais escuro que os vizinhos.

| Situação | Resposta com centro $-4$ |
|---|---:|
| centro semelhante aos vizinhos | próxima de zero |
| centro mais claro | negativa |
| centro mais escuro | positiva |

O sinal seria invertido com o kernel oposto:

$$
\begin{bmatrix}
0&-1&0\\
-1&4&-1\\
0&-1&0
\end{bmatrix}
$$

Os dois kernels detectam as mesmas variações; o que muda é o sinal.

## 7. Comportamento em uma borda

Considere uma transição do escuro para o claro:

$$
[0,0,0,255,255,255]
$$

A primeira derivada indica a intensidade da mudança. A segunda derivada tende a produzir respostas de sinais opostos nos dois lados da transição.

Assim, uma borda pode aparecer como:

- resposta positiva de um lado;
- resposta negativa do outro;
- passagem por zero entre elas.

Essa passagem é denominada **cruzamento por zero**. Métodos clássicos podem procurar esses cruzamentos depois de suavizar a imagem.

## 8. Por que não armazenar diretamente em 8 bits?

Uma imagem de 8 bits sem sinal armazena:

$$
0 \leq I \leq 255
$$

O Laplaciano pode produzir valores negativos, valores maiores que 255 e valores próximos de zero. Se uma resposta como $-200$ for gravada diretamente em uma imagem de 8 bits, a informação do sinal será perdida.

Durante o cálculo, é preferível utilizar:

- double ou float;
- CV_32F ou CV_64F em C++;
- double em Java;
- float32 ou float64 em Python/NumPy.

A resposta bruta deve ser preservada antes da visualização.

## 9. Formas de visualizar

### 9.1 Valor absoluto

$$
V(x,y)=|L(x,y)|
$$

Essa visualização mostra a intensidade da resposta, mas perde o sinal.

### 9.2 Deslocamento por 128

$$
V(x,y)=L(x,y)+128
$$

Depois, o resultado é limitado a $[0,255]$:

- 128 representa resposta zero;
- valores menores que 128 representam respostas negativas;
- valores maiores que 128 representam respostas positivas.

### 9.3 Normalização

Também é possível mapear o menor e o maior valor para $[0,255]$. Isso melhora a visibilidade, mas altera a escala absoluta. A transformação deve ser declarada no relatório.

## 10. Uso para realce

Para o kernel com centro $-4$, uma forma de realce é:

$$
g(x,y)=f(x,y)-\lambda L(x,y)
$$

em que:

- $f$ é a imagem original;
- $L$ é a resposta Laplaciana bruta;
- $\lambda$ controla a intensidade;
- $g$ é a imagem realçada.

Com $\lambda=1$:

$$
g=f-L
$$

Substituindo a expressão do Laplaciano:

$$
g=
5f(x,y)
-f(x-1,y)
-f(x+1,y)
-f(x,y-1)
-f(x,y+1)
$$

Isso equivale ao kernel:

$$
K_R=
\begin{bmatrix}
0&-1&0\\
-1&5&-1\\
0&-1&0
\end{bmatrix}
$$

É importante combinar a imagem com a resposta bruta. Se o Laplaciano for saturado antes, parte das informações negativas será perdida.

## 11. Variante com oito vizinhos

Outra máscara considera também as diagonais:

$$
K_{L8}=
\begin{bmatrix}
1&1&1\\
1&-8&1\\
1&1&1
\end{bmatrix}
$$

A soma continua sendo zero. Essa variante responde às oito posições ao redor do centro, mas também pode ser mais sensível a detalhes e ruído.

| Kernel | Vizinhança | Coeficiente central |
|---|---|---:|
| Laplaciano de 4 vizinhos | ortogonais | $-4$ |
| Laplaciano de 8 vizinhos | ortogonais e diagonais | $-8$ |

## 12. Sensibilidade ao ruído

Derivadas amplificam variações rápidas. Como o Laplaciano é uma derivada de segunda ordem, ele é especialmente sensível ao ruído.

Um pixel ruidoso isolado pode parecer uma mudança importante. Por isso, é comum suavizar antes:

$$
f
\longrightarrow
\text{filtro Gaussiano}
\longrightarrow
\text{Laplaciano}
$$

Essa ideia está relacionada ao **Laplaciano do Gaussiano** (*Laplacian of Gaussian — LoG*).

A suavização reduz ruído, mas também pode eliminar detalhes pequenos. O tamanho do kernel e o desvio-padrão do Gaussiano determinam a escala das bordas preservadas.

## 13. Comparação com Sobel

| Característica | Laplaciano | Sobel |
|---|---|---|
| Ordem da derivada | segunda | primeira |
| Resultado | uma resposta escalar | $G_x$ e $G_y$ |
| Direção da borda | não fornece diretamente | permite estimar |
| Orientação | aproximadamente isotrópica | separa horizontal e vertical |
| Sensibilidade ao ruído | maior | geralmente menor |
| Uso comum | detalhes, cruzamentos por zero e realce | magnitude e direção do gradiente |

Sobel permite estimar:

$$
\theta=\operatorname{atan2}(G_y,G_x)
$$

O Laplaciano não fornece diretamente a orientação da borda.

## 14. Pseudocódigo

Considerando a máscara de quatro vizinhos:

    FUNÇÃO laplaciano(entrada, estrategiaBorda):

        kernel ←
            [ 0,  1,  0 ]
            [ 1, -4,  1 ]
            [ 0,  1,  0 ]

        respostaBruta ← convolucao(
            entrada,
            kernel,
            fator = 1,
            estrategiaBorda
        )

        RETORNAR respostaBruta

Para produzir o realce:

    FUNÇÃO realcarComLaplaciano(
        entrada,
        lambda,
        estrategiaBorda
    ):

        resposta ← laplaciano(
            entrada,
            estrategiaBorda
        )

        criar realcada com as dimensões da entrada

        PARA cada posição (x,y):

            valor ← entrada[y,x] -
                    lambda × resposta[y,x]

            realcada[y,x] ← limitar(valor, 0, 255)

        RETORNAR realcada

## 15. Cuidados para o laboratório

- preservar a resposta bruta em tipo assinado ou real;
- não aplicar valor absoluto antes da análise;
- não saturar antes de calcular o realce;
- documentar o sinal do kernel escolhido;
- testar uma imagem constante;
- testar um pixel claro isolado;
- testar um pixel escuro isolado;
- testar um degrau de intensidade;
- comparar as estratégias de borda;
- distinguir a resposta bruta da imagem preparada para visualização.

## 16. Síntese

O Laplaciano calcula a diferença entre o pixel central e sua vizinhança por meio de uma aproximação da segunda derivada.

- região constante produz resposta zero;
- centro diferente da vizinhança produz grande magnitude;
- o sinal indica o sentido da diferença conforme o kernel escolhido;
- uma borda tende a produzir respostas de sinais opostos;
- o realce combina a resposta bruta com a imagem original;
- ruído e detalhes finos também são amplificados.
