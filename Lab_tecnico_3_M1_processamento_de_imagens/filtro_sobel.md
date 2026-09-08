# Filtro de Sobel: gradiente, magnitude e direção das bordas

## 1. Ideia central

O filtro de Sobel procura **variações rápidas de intensidade** na imagem. Essas variações costumam ocorrer nas transições entre regiões claras e escuras e, por isso, são usadas como evidência de bordas.

Em vez de produzir diretamente uma única resposta, Sobel calcula duas componentes:

- $G_x$: variação da intensidade na direção horizontal, isto é, ao longo do eixo $x$;
- $G_y$: variação da intensidade na direção vertical, isto é, ao longo do eixo $y$.

Essas componentes formam uma aproximação do **gradiente** da imagem:

$$
\nabla I(x,y) =
\begin{bmatrix}
G_x(x,y) \\
G_y(x,y)
\end{bmatrix}
$$

O gradiente aponta para a direção em que a intensidade aumenta mais rapidamente. Seu módulo indica a intensidade da transição.

> Importante: $G_x$ e $G_y$ descrevem a direção do gradiente, que é aproximadamente perpendicular à borda observada.

## 2. Kernels de Sobel

Neste material, usaremos os kernels:

$$
K_x =
\begin{bmatrix}
-1 & 0 & 1 \\
-2 & 0 & 2 \\
-1 & 0 & 1
\end{bmatrix}
$$

$$
K_y =
\begin{bmatrix}
-1 & -2 & -1 \\
0 & 0 & 0 \\
1 & 2 & 1
\end{bmatrix}
$$

Adotamos a convenção didática de chamar de **convolução** a aplicação direta dos coeficientes apresentados, sem girar o kernel em $180^\circ$. Matematicamente, essa operação corresponde à correlação. Se os kernels forem girados, os sinais das respostas serão invertidos, mas a magnitude das bordas continuará a mesma.

Para cada pixel $(x,y)$, a âncora do kernel é alinhada a esse pixel. Os valores da vizinhança são multiplicados pelos coeficientes de posição correspondente e os produtos são somados:

$$
G_x(x,y) = \sum_{v=-1}^{1}\sum_{u=-1}^{1}
K_x(u,v)\,I(x+u,y+v)
$$

$$
G_y(x,y) = \sum_{v=-1}^{1}\sum_{u=-1}^{1}
K_y(u,v)\,I(x+u,y+v)
$$

Aqui, $u$ e $v$ são coordenadas relativas ao centro do kernel.

## 3. Por que $G_x$ evidencia bordas verticais?

No kernel $K_x$, os coeficientes da coluna esquerda são negativos, os da coluna central são zero e os da coluna direita são positivos. Portanto, sua resposta se comporta como uma comparação ponderada entre os lados direito e esquerdo da vizinhança:

$$
G_x \approx \text{lado direito} - \text{lado esquerdo}
$$

Se a intensidade muda da esquerda para a direita, $G_x$ tem grande módulo. Essa mudança ocorre ao atravessar uma **borda vertical**.

De forma análoga, $K_y$ compara a parte inferior com a parte superior:

$$
G_y \approx \text{parte inferior} - \text{parte superior}
$$

Assim, $G_y$ responde fortemente quando atravessamos uma **borda horizontal**.

| Componente | Variação medida | Borda evidenciada |
|---|---|---|
| $G_x$ | esquerda $\rightarrow$ direita | vertical |
| $G_y$ | cima $\rightarrow$ baixo | horizontal |

## 4. Derivada e suavização no mesmo kernel

O Sobel combina uma aproximação de derivada com uma pequena suavização. O kernel $K_x$ pode ser escrito como o produto de dois filtros unidimensionais:

$$
K_x =
\begin{bmatrix}
1 \\ 2 \\ 1
\end{bmatrix}
\begin{bmatrix}
-1 & 0 & 1
\end{bmatrix}
$$

A sequência $[-1,0,1]$ calcula uma diferença central ao longo de $x$, enquanto $[1,2,1]^T$ suaviza ao longo de $y$.

Analogamente:

$$
K_y =
\begin{bmatrix}
-1 \\ 0 \\ 1
\end{bmatrix}
\begin{bmatrix}
1 & 2 & 1
\end{bmatrix}
$$

Essa suavização reduz um pouco a influência do ruído, embora não elimine a necessidade de uma suavização gaussiana prévia em imagens muito ruidosas.

## 5. Resposta em uma região constante

Em ambos os kernels, a soma dos coeficientes é zero. Se todos os pixels da vizinhança possuem o mesmo valor $c$, então:

$$
G_x = c\sum K_x = 0
$$

$$
G_y = c\sum K_y = 0
$$

Portanto, regiões uniformes produzem resposta zero ou muito próxima de zero.

## 6. Exemplo numérico: borda vertical

Considere a vizinhança:

$$
I_N =
\begin{bmatrix}
0 & 0 & 255 \\
0 & 0 & 255 \\
0 & 0 & 255
\end{bmatrix}
$$

Aplicando $K_x$ diretamente:

$$
G_x =
(-1\cdot0)+(0\cdot0)+(1\cdot255)
+(-2\cdot0)+(0\cdot0)+(2\cdot255)
+(-1\cdot0)+(0\cdot0)+(1\cdot255)
$$

$$
G_x = 255 + 510 + 255 = 1020
$$

Para $K_y$, as contribuições de cima e de baixo se anulam:

$$
G_y = 0
$$

O resultado indica uma borda vertical forte e uma intensidade que cresce da esquerda para a direita.

## 7. Exemplo numérico: borda horizontal

Considere agora:

$$
I_N =
\begin{bmatrix}
0 & 0 & 0 \\
0 & 0 & 0 \\
255 & 255 & 255
\end{bmatrix}
$$

Nesse caso:

$$
G_x = 0
$$

$$
G_y = 255 + 510 + 255 = 1020
$$

A resposta indica uma borda horizontal forte e uma intensidade que cresce de cima para baixo.

## 8. Como interpretar o sinal

Com os kernels apresentados e a aplicação direta:

- $G_x > 0$: a intensidade tende a aumentar da esquerda para a direita;
- $G_x < 0$: a intensidade tende a diminuir da esquerda para a direita;
- $G_y > 0$: a intensidade tende a aumentar de cima para baixo;
- $G_y < 0$: a intensidade tende a diminuir de cima para baixo.

O sinal carrega informação sobre o sentido da transição. Aplicar valor absoluto muito cedo elimina essa informação.

## 9. Magnitude do gradiente

Depois de calcular $G_x$ e $G_y$, podemos combiná-los. A magnitude euclidiana é:

$$
M_2(x,y) = \sqrt{G_x(x,y)^2 + G_y(x,y)^2}
$$

Ela representa o comprimento do vetor gradiente. Uma aproximação mais barata é:

$$
M_1(x,y) = |G_x(x,y)| + |G_y(x,y)|
$$

As duas formas são válidas, mas geram escalas diferentes. Portanto, limiares escolhidos para $M_1$ não devem ser reutilizados automaticamente em $M_2$.

## 10. Direção do gradiente e orientação da borda

A direção do gradiente é calculada por:

$$
\theta(x,y) = \operatorname{atan2}\bigl(G_y(x,y),G_x(x,y)\bigr)
$$

A função $\operatorname{atan2}$ considera os sinais das duas componentes e identifica corretamente o quadrante do vetor.

Entretanto, $\theta$ é a direção de maior crescimento da intensidade, e não a direção na qual a borda se estende. A orientação da borda é aproximadamente perpendicular ao gradiente:

$$
\theta_{\text{borda}} = \theta + \frac{\pi}{2}
$$

Como orientações de borda normalmente são consideradas equivalentes após uma rotação de $180^\circ$, o resultado pode ser normalizado para um intervalo como $[0,\pi)$.

## 11. Tipos numéricos e faixa de valores

Para uma imagem de 8 bits, cada pixel está entre 0 e 255. O maior valor positivo de uma componente de Sobel pode atingir:

$$
4\cdot255 = 1020
$$

Assim, $G_x$ e $G_y$ podem assumir aproximadamente valores entre $-1020$ e $1020$. Um tipo unsigned de 8 bits não consegue representar valores negativos nem valores acima de 255.

Durante o cálculo, use um tipo com sinal e faixa suficiente, como inteiro de 16 ou 32 bits, float ou double. Não converta para 8 bits antes de calcular a magnitude.

## 12. Exibição do resultado

As respostas brutas não são diretamente uma imagem de 8 bits. Algumas opções de visualização são:

- exibir $|G_x|$ e $|G_y|$ para mostrar a força das transições;
- normalizar a faixa observada para $[0,255]$;
- somar um deslocamento para representar sinais negativos e positivos;
- aplicar um limiar sobre a magnitude para obter um mapa binário de bordas.

É importante registrar qual transformação foi usada. A imagem exibida pode não conter mais os valores brutos do gradiente.

## 13. Tratamento das bordas da imagem

Um kernel $3\times3$ ultrapassa a imagem quando sua âncora está na primeira ou na última linha ou coluna. Duas estratégias discutidas no laboratório são:

### 13.1 Copy

A saída começa como uma cópia da entrada. A operação é calculada apenas onde todo o kernel cabe na imagem. A moldura externa permanece com os valores originais.

Para um kernel $3\times3$, processamos:

$$
1 \le x \le W-2
$$

$$
1 \le y \le H-2
$$

### 13.2 Replicate

Todos os pixels são processados. Quando uma coordenada da vizinhança ultrapassa a imagem, usamos o pixel válido mais próximo:

$$
x' = \min\bigl(\max(x,0),W-1\bigr)
$$

$$
y' = \min\bigl(\max(y,0),H-1\bigr)
$$

Aqui, $W$ é a largura da imagem e $H$ é a altura. Essa estratégia replica os valores da borda para fora do domínio válido.

## 14. Pseudocódigo

O cálculo pode reutilizar uma função genérica de convolução e preservar as respostas brutas:

    ALGORITMO sobel(entrada, estrategiaBorda)
        kernelGx ← matriz 3×3 com [-1,0,1; -2,0,2; -1,0,1]
        kernelGy ← matriz 3×3 com [-1,-2,-1; 0,0,0; 1,2,1]

        gxBruto ← convolucao(entrada, kernelGx, ancora=(1,1), estrategiaBorda)
        gyBruto ← convolucao(entrada, kernelGy, ancora=(1,1), estrategiaBorda)

        criar magnitudeL1 com as dimensões da entrada
        criar magnitudeL2 com as dimensões da entrada
        criar direcao com as dimensões da entrada

        PARA y DE 0 ATÉ altura(entrada)-1
            PARA x DE 0 ATÉ largura(entrada)-1
                gx ← gxBruto[y,x]
                gy ← gyBruto[y,x]

                magnitudeL1[y,x] ← abs(gx) + abs(gy)
                magnitudeL2[y,x] ← sqrt(gx*gx + gy*gy)
                direcao[y,x] ← atan2(gy,gx)
            FIM PARA
        FIM PARA

        RETORNAR gxBruto, gyBruto, magnitudeL1, magnitudeL2, direcao
    FIM ALGORITMO

Se a direção não for necessária, ela pode ser omitida. Para fins didáticos, calcular duas convoluções separadas deixa claro que $G_x$ e $G_y$ são componentes independentes do mesmo gradiente.

## 15. Relação com o Laplaciano

| Característica | Sobel | Laplaciano |
|---|---|---|
| Ordem da derivada | primeira | segunda |
| Resposta | duas componentes, $G_x$ e $G_y$ | uma resposta escalar |
| Informação direcional | sim | não diretamente |
| Sensibilidade ao ruído | alta, mas com leve suavização | geralmente maior |
| Uso típico | magnitude e orientação de bordas | realce e detecção de mudanças rápidas |

O Sobel indica força e direção da variação. O Laplaciano mede como a taxa de variação muda e costuma responder dos dois lados de uma transição.

## 16. Testes úteis para a implementação

1. **Imagem constante:** $G_x=0$ e $G_y=0$ no interior.
2. **Degrau vertical:** $|G_x|$ alto e $G_y$ próximo de zero.
3. **Degrau horizontal:** $|G_y|$ alto e $G_x$ próximo de zero.
4. **Degrau diagonal:** as duas componentes devem contribuir.
5. **Transição invertida:** o sinal deve inverter, mas a magnitude deve permanecer igual.
6. **Bordas da imagem:** verificar separadamente as estratégias copy e replicate.

## 17. Erros comuns

- dizer que $G_x$ detecta bordas horizontais: ele mede a variação horizontal e evidencia principalmente bordas verticais;
- confundir a direção do gradiente com a orientação da borda;
- armazenar $G_x$ ou $G_y$ diretamente em uint8;
- saturar ou aplicar valor absoluto antes de terminar os cálculos;
- comparar limiares de $M_1$ e $M_2$ como se as escalas fossem idênticas;
- esquecer que girar os kernels, como na convolução matemática estrita, inverte os sinais;
- processar as bordas sem declarar qual estratégia foi usada.

## 18. Síntese

O Sobel aproxima o gradiente da imagem com dois kernels $3\times3$. $G_x$ mede variações ao longo de $x$ e evidencia bordas verticais; $G_y$ mede variações ao longo de $y$ e evidencia bordas horizontais. O módulo combina as duas respostas para estimar a força da borda, enquanto $\operatorname{atan2}(G_y,G_x)$ fornece a direção do gradiente. A implementação deve preservar valores com sinal, tratar explicitamente as bordas e converter para 8 bits apenas na etapa de visualização.
