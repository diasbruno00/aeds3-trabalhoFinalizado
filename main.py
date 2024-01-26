import heapq
import networkx as net
from collections import deque
import tkinter as tk
from tkinter import filedialog
from PIL import ImageDraw
from pathlib import Path
import sys
import re
from PIL import Image, ImageDraw


def adicionandoNosAoGrafo(grafo, imagem, nome_arquivo):
   try:
        largura, altura = imagem.size
        andar = int(re.search(r'\d+', nome_arquivo).group())
        for y in range(altura):
            for x in range(largura):
               grafo.add_node((y, x, andar))
   except Exception as erro:
        print(erro)

def dijkstra(G, inicio, no_verde):
    try:
        fila = [(0, inicio, [])]
        visitados = set()

        while fila:
            (peso, no, caminho) = heapq.heappop(fila)
            if no not in visitados:
                caminho = caminho + [no]
                visitados.add(no)
                if no == no_verde:
                    return caminho  # Retorna o caminho e a soma dos pesos
                for vizinho, dados in G[no].items():
                    if vizinho not in visitados:
                        # Verifique se os nós estão no mesmo andar ou se o andar vizinho é imediatamente superior ou inferior
                        if no[2] == vizinho[2] or abs(no[2] - vizinho[2]) == 1:
                            novo_peso = peso + dados['weight']
                        else:
                            novo_peso = peso + 5
                        heapq.heappush(fila, (novo_peso, vizinho, caminho))
        return None
    except Exception as e:
        print("Deu erro na função disjtra: ", e)

def verificandoAndar(nome_arquivo):
    return int(re.search(r'\d+', nome_arquivo).group())

def adicionandoArestas(grafo, y, x, andar, largura, altura, pixels):
    # Verifique os vizinhos (cima, baixo, esquerda, direita, cima, baixo)
    for dy, dx, dz in [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)]:
        ny, nx, nz = y + dy, x + dx, andar + dz
        # Certifique-se de que os vizinhos estão dentro dos limites da imagem
        if 0 <= ny < altura and 0 <= nx < largura:
            # Calcule os índices unidimensionais
            idx = y * largura + x
            nidx = ny * largura + nx
            # Verifique se nenhum dos dois pixels é preto
            if pixels[idx] != (0, 0, 0) and pixels[nidx] != (0, 0, 0):
                adicionandoArestasCondicional(grafo, y, x, andar, ny, nx, nz, idx, nidx, pixels)

def adicionandoArestasCondicional(grafo, y, x, andar, ny, nx, nz, idx, nidx, pixels):
    # Verifique se os pixels estão no mesmo andar ou se o andar vizinho é imediatamente superior ou inferior
    if pixels[idx][2] == pixels[nidx][2] or abs(pixels[idx][2] - pixels[nidx][2]) == 1:
        # Verifique se os pixels são cinza escuro
        if pixels[idx] == (128, 128, 128) and pixels[nidx] == (128, 128, 128):
            grafo.add_edge((y, x, andar), (ny, nx, nz), weight=4)
        # Verifique se os pixels são cinza claro
        elif pixels[idx] == (196, 196, 196) and pixels[nidx] == (196, 196, 196):
            grafo.add_edge((y, x, andar), (ny, nx, nz), weight=2)
        # Verifique se os pixels são brancos
        else:
            grafo.add_edge((y, x, andar), (ny, nx, nz), weight=1)
    # Verifique se os pixels estão em andares diferentes
    elif abs(pixels[idx][2] - pixels[nidx][2]) > 1:
        grafo.add_edge((y, x, andar), (ny, nx, nz), weight=5)

def adicionandoArestasAosNosApartirDeUmaValidacao(grafo, imagem, pixels, nome_arquivo):
    try:
        largura, altura = imagem.size  
        andar = verificandoAndar(nome_arquivo)
        for y in range(altura):
            for x in range(largura):
                adicionandoArestas(grafo, y, x, andar, largura, altura, pixels)
    except Exception as erro:
        print(erro)


def buscaEmLargura(G, inicio, alvo):
    fila = deque([(inicio, [])])
    visitados = set()

    while fila:
        no, caminho = fila.popleft()
        if no == alvo:
            return caminho
        if no not in visitados:
            visitados.add(no)
            vizinhos = list(G.neighbors(no))
            fila.extend((vizinho, caminho + [vizinho]) for vizinho in vizinhos)
    
    return None


def exibirCaminho(caminho, no_vermelho):
    for passo in caminho:
        if passo[0] < no_vermelho[0]:
            print("↑", end=" ")
        elif passo[0] > no_vermelho[0]:
            print("↓", end=" ")
        elif passo[1] < no_vermelho[1]:
            print("←", end=" ")
        elif passo[1] > no_vermelho[1]:
            print("→", end=" ")
        no_vermelho = passo
    print()


def buscandoNoVermelho(pixels, nome_arquivo):
    largura, altura = img.size
    andar = int(re.search(r'\d+', nome_arquivo).group())
    for y in range(altura):
        for x in range(largura):
            if pixels[y * largura + x] == (255, 0, 0):
                return (y, x, andar)

def buscandoNoVerde(pixels, nome_arquivo):
    andar = int(re.search(r'\d+', nome_arquivo).group())
    largura, altura = img.size
    for y in range(altura):
        for x in range(largura):
            if pixels[y * largura + x] == (0, 255, 0):
                return (y, x, andar)


def listaDeNosVerdes(pixels, nome_arquivo):
    largura, altura = img.size
    andar = int(re.search(r'\d+', nome_arquivo).group())
    nos_verdes = []
    for y in range(altura):
        for x in range(largura):
            if pixels[y * largura + x] == (0, 255, 0):
                nos_verdes.append((y, x, andar))
    return nos_verdes

def escolher_arquivo():
    root = tk.Tk()
    root.withdraw()
    root.title("Escolha seu arquivo")
    arquivo = filedialog.askopenfilename()
    return arquivo


def buscarPasta():
    nomePasta = str(input('Informe a pasta contendo o(s) arquivo(s) bitmap: '))
    listaArquivos = list(Path(nomePasta).rglob('*.bmp'))
    return listaArquivos


def imagemAtualizada(imagem, caminho):
    try:
        copia_imagem = imagem.copy()
        desenho = ImageDraw.Draw(copia_imagem)
        
        for no1, no2 in zip(caminho, caminho[1:]):
            coordenada1 = (no1[1], no1[0])  # Extrai as coordenadas (x, y) do nó 1
            coordenada2 = (no2[1], no2[0])  # Extrai as coordenadas (x, y) do nó 2
            desenho.line([coordenada1, coordenada2], fill=(255, 0, 127), width=1)  
    
        copia_imagem.show()
    except Exception as erro:
        print("Ocorreu um erro na função de exibição: ", erro)

def buscandoMenorCaminho(listaNosVerdes, no_vermelho, G):
    try:
        listaDeCaminhos = []
        for noVerde in listaNosVerdes:
            caminho = buscaEmLargura(G, no_vermelho, noVerde)
            listaDeCaminhos.append(caminho)
        
        return listaDeCaminhos
    except Exception as error:
        print(error)
            

def melhorCaminho(listaNosVerdes, no_vermelho, G):
    try:
        listaDeCaminhos = buscandoMenorCaminho(listaNosVerdes, no_vermelho, G)
        menorCaminho = min(listaDeCaminhos, key=len)
        return menorCaminho
    except Exception as error:
        print(error)

if __name__ == "__main__":

        
        while True:

            try:
                            
                print("\n")
                print("O laço sera encerrado caso o usuario venha digitar 'sair' ou digite o nome da pasta errada \n")
                
                nomeArquivo = buscarPasta()

                if str(nomeArquivo[0]) == "sair":
                    sys.exit()

                elif len(nomeArquivo) == 1:

                    nomeArquivo = str(nomeArquivo[0])
                
                    print(f'Caminho do arquivo selecionado: {nomeArquivo} \n')

                    img = Image.open(nomeArquivo)

                    img_rgb = img.convert('RGB')

                    pixels = list(img_rgb.getdata())

                    G = net.Graph()

                    print("Processando... \n")

                    adicionandoNosAoGrafo(G,img,nomeArquivo)
                    adicionandoArestasAosNosApartirDeUmaValidacao(G,img, pixels, nomeArquivo)
                  
                    
                    no_vermelho = buscandoNoVermelho(pixels, nomeArquivo)
                    listaNosVerdes = listaDeNosVerdes(pixels, nomeArquivo)


                    if no_vermelho is not None and listaNosVerdes is not None:
                        
                        if nomeArquivo == "toyLaydown\\toy_0.bmp":
                                
                                                            
                                menorCaminho = melhorCaminho(listaNosVerdes, no_vermelho, G)

                                #menorCamaninho[-1] e o ultimo elemento da lista que e o no verde
                                caminho = buscaEmLargura(G, no_vermelho, menorCaminho[-1])

                                                    
                                if caminho is not None:
                                    print("É possivel deslocar o equipamento: \n")
                                    exibirCaminho(caminho, no_vermelho)
                                    imagemAtualizada(img, caminho)
                                                            
                                else:
                                    print("Não é possível descolar esse equipamento. \n")

                        elif nomeArquivo == "toyGrey\\toy_0.bmp":
                                
                       
                                caminho = dijkstra(G, no_vermelho, listaNosVerdes[0])
      
                                if caminho is not None:
                                    print("É possivel deslocar o equipamento: \n")
                                    exibirCaminho(caminho, no_vermelho)
                                    imagemAtualizada(img, caminho)
                                                            
                                else:
                                    print("Não é possível descolar esse equipamento. \n")


                else:
                     
                     valorAtualNoVerde =  ""
                     valorAtualNoVerMelho = ""

                     G = net.Graph()

                     for nome in nomeArquivo:
                        nome = str(nome)
                        print(f'Processando arquivo: {nome} \n')

                        img = Image.open(nome)
                        img_rgb = img.convert('RGB')
                        pixels = list(img_rgb.getdata())

                        adicionandoNosAoGrafo(G, img, nome)

                        adicionandoArestasAosNosApartirDeUmaValidacao(G, img,  pixels, nome)

                        no_vermelho = buscandoNoVermelho(pixels, nome)

                        if no_vermelho != None:
                            valorAtualNoVerMelho = no_vermelho

                        no_verde = buscandoNoVerde(pixels, nome)

                        if no_verde != None:
                            valorAtualNoVerde = no_verde

                     caminho = dijkstra(G, valorAtualNoVerMelho, valorAtualNoVerde)

                     exibirCaminho(caminho, valorAtualNoVerMelho)

            except Exception as e:
                print(f'Programa finalizado \n')
                print(e)
                break