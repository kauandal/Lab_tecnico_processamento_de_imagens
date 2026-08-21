import cv2 as cv
import numpy as np
import os

# só para garantir que a pasta de saída exista
os.makedirs("saidas", exist_ok=True)

def transformar_em_cinza(img):
    if len(img.shape) == 3:
        print("Fazendo a Conversão manual para níveis de cinza")
        altura = img.shape[0]
        largura = img.shape[1]

        ponderada = np.zeros((altura, largura), dtype=np.uint8)

        for i in range(altura):
            for j in range(largura):
                ponderada[i][j] = img[i][j][0]*0.114 + img[i][j][1]*0.587 + img[i][j][2]*0.299

        cv.imwrite("saidas/gray.weighted.png", ponderada)
        return ponderada

    else:
        print("Imagem em escala de cinza, não é possível transformar em cinza novamente")
        return

def brilho(img):
    altura = img.shape[0]
    largura = img.shape[1]
    brilho_positivo = np.zeros((altura, largura), dtype=np.uint8)
    brilho_negativo = np.zeros((altura, largura), dtype=np.uint8)
    b = 50

    print("brilho positivo e negativo criados")

    for i in range(altura):
            for j in range(largura):

                valor = int(img[i, j])

                b_positivo = valor + b
                b_negativo = valor - b
            

                if b_positivo > 255:
                    b_positivo = 255

                if b_negativo < 0:
                    b_negativo = 0

                brilho_positivo[i,j] = b_positivo
                brilho_negativo[i,j] = b_negativo

    cv.imwrite("saidas/brilho_positivo.png", brilho_positivo)
    cv.imwrite("saidas/brilho_negativo.png", brilho_negativo)

def contraste(img):
    altura, largura = img.shape
    aMeio = np.zeros((altura, largura), dtype=np.uint8)
    a1 = np.zeros((altura, largura), dtype=np.uint8)
    a1Meio = np.zeros((altura, largura), dtype=np.uint8)

    for i in range(altura):
        for j in range(largura):
            valor = float(img[i, j])

            # Arredondamento e limitação de intervalo para todos os fatores
            v_05 = int(np.round(0.5 * (valor - 128) + 128))
            v_10 = int(np.round(1.0 * (valor - 128) + 128))
            v_15 = int(np.round(1.5 * (valor - 128) + 128))

            aMeio[i, j] = np.clip(v_05, 0, 255)
            a1[i, j] = np.clip(v_10, 0, 255)
            a1Meio[i, j] = np.clip(v_15, 0, 255)

    cv.imwrite("saidas/a0_5.png", aMeio)
    cv.imwrite("saidas/a1_0.png", a1)
    cv.imwrite("saidas/a1_5.png", a1Meio)

def negativo(img):
    altura = img.shape[0]
    largura = img.shape[1]
    negativo = np.zeros((altura, largura), dtype=np.uint8)
    print("negativo criada")
    for i in range(altura):
            for j in range(largura):
                negativo[i,j] = 255 - img[i,j]
    cv.imwrite("saidas/negative.png", negativo)
    return negativo

def limiarizacao(img, limiar1=128, limiar2=64):
    # Validação de limiares fora do intervalo esperado
    for l in [limiar1, limiar2]:
        if not (0 <= l <= 255):
            raise ValueError(
                f"Limiar {l} fora do intervalo válido (0 a 255)."
            )

    altura, largura = img.shape
    limiarizacao_1 = np.zeros((altura, largura), dtype=np.uint8)
    limiarizacao_2 = np.zeros((altura, largura), dtype=np.uint8)

    for i in range(altura):
        for j in range(largura):
            valor = int(img[i, j])
            limiarizacao_1[i, j] = 255 if valor >= limiar1 else 0
            limiarizacao_2[i, j] = 255 if valor >= limiar2 else 0

    cv.imwrite(f"saidas/limiarizacao_{limiar1}.png", limiarizacao_1)
    cv.imwrite(f"saidas/limiarizacao_{limiar2}.png", limiarizacao_2)
    return limiarizacao_1, limiarizacao_2

def histograma(img, titulo):

    altura = img.shape[0]
    largura = img.shape[1]
    histograma = np.zeros((256), dtype=int)

    for i in range(altura):
         for j in range(largura):
              valor = int(img[i, j])
              histograma[valor] += 1

    print("Histograma calculado para a imagem: ", titulo)

    with open(f"saidas/histograma_{titulo}.txt", "w", encoding="utf-8") as arquivo:

        arquivo.write("intensidade,quantidade\n")
        for i in range(256):

            arquivo.write(f"{i}, {histograma[i]}\n")

def rodar_teste_sistetico(img):
    altura = img.shape[0]
    largura = img.shape[1]
    teste_sintetico = np.zeros((altura, largura), dtype=np.uint8)

    for i in range(altura):
        for j in range(largura):
            if (i < altura/2 and j < largura/2) or (i >= altura/2 and j >= largura/2):
                teste_sintetico[i,j] = 255
            else:
                teste_sintetico[i,j] = 0

    cv.imwrite("saidas/teste_sintetico.png", teste_sintetico)
    return teste_sintetico

def main():
    img = cv.imread("aura.png")
    saida = "saidas/saida.png"
    img = transformar_em_cinza(img)
    brilho(img)
    contraste(img)
    x = negativo(img)
    y, z = limiarizacao(img, 128, 64)
    histograma(img, "histograma da imagem original")
    histograma(x, "histograma do negativo")
    histograma(y, "histograma da limiarização 128")
    histograma(z, "histograma da limiarização 64")

    teste_sintetico = np.zeros((4, 4), dtype=np.uint8)
    rodar_teste_sistetico(img)

if __name__ == "__main__":
    main()
