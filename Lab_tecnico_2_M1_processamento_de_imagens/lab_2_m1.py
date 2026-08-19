import cv2 as cv
import numpy as np


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
    ponderada = np.zeros((altura, largura), dtype=np.uint8)
    brilho_positivo = np.zeros((altura, largura), dtype=np.uint8)
    brilho_negativo = np.zeros((altura, largura), dtype=np.uint8)
    b = 50

    print("brilho positivo criada")

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


def main():
    img = cv.imread("aura.png")
    saida = "saidas/saida.png"
    img = transformar_em_cinza(img)
    brilho(img)
    
if __name__ == "__main__":
    main()

