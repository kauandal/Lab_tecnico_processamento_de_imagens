Kauan Rocha Dalfovo

Consegui desenvolver todas as atividades propostas ao decorrer da semana. Com a ajuda do .md do lab 2 fica bem mais fácil, pois ele já entrega a forma que você deve alterar os pixeis para formar a imagem, fiz a transformação para cinza com a media ponderada para diminuir o numero de canais para 1 e a partir dessa fiz todas as alterações.

Tive alguns problemas com o ajuste de brilho pois as imagens não estavam em uint8 e, após colocar nesse formato, estava estourando alguns pixeis que passavam de 255 e acabavam resultando em overflow que acarretava o valor a "dar a volta". Precisei fazer uma pesquisa para conseguir resolver e chegar no resultado esperado.

Rodei os testes com algumas imagens que encontrei na internet e todas deram o resultado esperado após essas correções. Como próximo passo, pretendo testar com imagens geradas por mim mesmo para já me adiantar na disciplina.