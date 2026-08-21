import cv2 as cv
import numpy as np
import os

# só para garantir que a pasta de saída exista
os.makedirs("saidas", exist_ok=True)

def inspecao_imagem(img):
    if len(img.shape) == 2:
        canais = 1
    elif len(img.shape) == 3:
        canais = img.shape[2]
    
    print("Dimensões da imagem: %s x %s" % (str(img.shape[1]), str(img.shape[0])))
    print("Tipo de dados: %s" % str(img.dtype))
    print("Número de canais: %d" % canais)
    print("Total de pixels: %d" % (img.size))

    if canais == 3:
        print("Imagem colorida (BGR)")
    else:
        print("Imagem em escala de cinza")

def criar_copia(img):
    altura = img.shape[0]
    largura = img.shape[1]
    copia = np.zeros((altura, largura, img.shape[2]))
    print("Cópia criada")
    for i in range(altura):
            for j in range(largura):
                copia[i,j] = img[i,j]
    cv.imwrite("saidas/copy.png", copia)

def separar_canais(img):
    if len(img.shape) == 3:
        print("Separando canais BGR")
        altura = img.shape[0]
        largura = img.shape[1]
        Blue = np.zeros((altura, largura, img.shape[2]))
        Green = np.zeros((altura, largura, img.shape[2]))
        Red = np.zeros((altura, largura, img.shape[2]))

        for i in range(altura):
            for j in range(largura):
                Blue[i][j] = [img[i][j][0],0,0]
                Green[i][j] = [0,img[i][j][1],0]
                Red[i][j] = [0,0,img[i][j][2]]

        cv.imwrite("saidas/channel_b.png", Blue)
        cv.imwrite("saidas/channel_g.png", Green)
        cv.imwrite("saidas/channel_r.png", Red)

    else:
        print("Imagem em escala de cinza, não é possível separar canais")
        return

def niveis_cinza(img):
    if len(img.shape) == 3:
        print("Fazendo a Conversão manual para níveis de cinza")
        altura = img.shape[0]
        largura = img.shape[1]
        simples = np.zeros((altura, largura, img.shape[2]))
        ponderada = np.zeros((altura, largura, img.shape[2]))

        for i in range(altura):
            for j in range(largura):
                simples[i][j] = (img[i][j][0] + img[i][j][1] + img[i][j][2])/3
                ponderada[i][j] = img[i][j][0]*0.114 + img[i][j][1]*0.587 + img[i][j][2]*0.299

        cv.imwrite("saidas/gray_average.png", simples)
        cv.imwrite("saidas/gray.weighted.png", ponderada)
        return ponderada

    else:
        print("Imagem em escala de cinza, não é possível transformar em cinza novamente")
        return

def quantizacao(imagem):
    img = niveis_cinza(imagem)

    altura = img.shape[0]
    largura = img.shape[1]

    quant = [2, 4, 8, 16]

    imagens_quantizadas = {}
      
    print("quantitativos criada")

    for q in quant:
        passo = 255/(q - 1)

        # Cria a imagem para esse nível de quantização
        quantizada = np.zeros(
            (altura, largura, img.shape[2]),
            dtype=np.uint8
        )

        for i in range(altura):
            for j in range(largura):
                indice = img[i][j][0] / passo
                indice = round(indice)

                # Volta do índice para o valor de cinza
                valor = round(indice * passo)

                quantizada[i][j] = valor
        # Guarda usando q como chave
        imagens_quantizadas[q] = quantizada   
    
    cv.imwrite("saidas/quant_16.png", imagens_quantizadas[16])
    cv.imwrite("saidas/quant_8.png", imagens_quantizadas[8])
    cv.imwrite("saidas/quant_4.png", imagens_quantizadas[4])
    cv.imwrite("saidas/quant_2.png", imagens_quantizadas[2])

def main():
    img = cv.imread("aura.png")
    saida = "saidas/saida.png"
    inspecao_imagem(img)
    criar_copia(img)
    separar_canais(img)
    niveis_cinza(img)
    quantizacao(img)
    
if __name__ == "__main__":
    main()

