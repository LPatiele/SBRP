# -*- coding: utf-8 -*-
from datetime import time
import random
import math
import copy

from models import Onibus, Escola, Parada, Garagem, Estudante


def distancia(localA, localB):# calcula distancia entre coordenadas geograficas
    dla = (float)(((localA.latitude - localB.latitude)/60)*1852) #diferença entre as latitudes em metros
    dlo =  (float)(((localA.longitude - localB.longitude)/60)*1852 )#diferença entre as longitudes em metros
    return math.sqrt(dla**2 + dlo**2) #distancia em metros 

def distanciaTestes(localA, localB):# calcula distancia pela matriz de distancia
    return localA.matrizDistancia[localB] #distancia em metros 

def printConj(conj, nome): # imprime na tela os conjuntos definidos ex: escolas, garagens, paradas,etc.
    print("Conjunto de ", nome)
    for i in conj:
        print(i)

def criarLRC(fatorRandomizacao, matrizCustos ): 
    # nessa função é onde realmente é criada a lista restrita de paradas 
    # candidatas a entrar na rota
    try:
        menorCusto= sorted(matrizCustos.values())[0]
        maiorCusto= sorted(matrizCustos.values())[len(matrizCustos)-1]
        grasp= menorCusto + fatorRandomizacao*(maiorCusto-menorCusto)
        lrc=[]
        for key in matrizCustos:
            if matrizCustos[key] <= grasp:
                lrc.append(key) # Acrescenta a parada na LRC
        return lrc
    except :
        return None
   
def listaRestritaDeCandidatosInicial(fatorRandomizacao, localSaidaOnibus, conjParadas):
    #LRCi
    # fatorRandomizacao = pode assumir valor entre 0 e 1 seve pra determinar o tamanho da lista LRC, onde se a =0 o metodo resá totalmente guloso e a= 1 totalmente aleatório
    matrizCustos={} # a estrutura de dados da matriz de custos é um diciionário onde a parada é a chave
    for parada in conjParadas:
        custo= distanciaTestes(localSaidaOnibus, parada) + distanciaTestes(parada, parada.escola)
        matrizCustos[ parada ] = custo
    return criarLRC(fatorRandomizacao, matrizCustos)
# Modificar apos o teste de  distanciaTestes para distancia  

def listaRestritaDeCandidatosPorEscola(fatorRandomizacao, paradaAnterior, conjParadas): 
    #LRCj
    # fatorRandomizacao = pode assumir valor entre 0 e 1 seve pra determinar o tamanho da lista LRC, onde se a =0 o metodo resá totalmente guloso e a= 1 totalmente aleatório
    matrizCustos={} # a estrutura de dados da matriz de custos é um diciionário onde a parada é a chave
    for parada in conjParadas:
        if parada.escola == paradaAnterior.escola:
            custo= distanciaTestes(paradaAnterior, parada) + distanciaTestes(parada, parada.escola)
            matrizCustos[ parada ]= custo
    return criarLRC(fatorRandomizacao, matrizCustos)
# Modificar apos o teste de  distanciaTestes para distancia

def tempoTrecho(distancia): # em minutos
    tempo = (float)(distancia/8.8888888889) # t=s/v , sendo s em metros e v em m/s e t em segundos
    return (float)(tempo/60.0)

def tempoEmbarque(qtAlunos): # em minutos
    tempo =(float)( 1.9 + 2.6 *qtAlunos) #em segundos
    return (float)(tempo/60)

def tempoDesembarque(qtAlunos): # em minutos
    tempo =(float)( 2.6 + 1.9 *qtAlunos) #em segundos
    return (float)(tempo/60)

def tempoDaRota(rota): 
    # somatória de tempo dos trechos, de embarques e desemarques de uma dada rota 
    tempo = 0.0
    paradaAnterior = None
    for parada in rota:
        if type(parada) == Parada:
            if paradaAnterior:
                tempo += tempoTrecho(distanciaTestes(paradaAnterior,parada))
                tempo += tempoEmbarque(parada.qtAlunos)
                tempo += tempoDesembarque(parada.qtAlunos)
            paradaAnterior = parada
    return tempo
        
def melhoriaDeRota(rota): # algoritmo 2-opt
    # a primeira parada da rota é a garagem e portanto não deve poder trocar a ordem de visita da garagem com uma parada
    # assim como a ultima parada é a escola visitada
    for i in  range(1, len(rota)-2):
        aux = copy.copy(rota)
        temp = aux[i]
        aux[i] = aux[i+1]
        aux[i+1] = temp
        print ("tempo aux : " ,tempoDaRota(aux), "tempo rota: ", tempoDaRota(rota))
        if tempoDaRota(rota) > tempoDaRota(aux): # se trocando a ordem de visita entre duas paradas o caminho ficar menor eu troco a ordem das paradas
            print("TROCOU  ", aux[i], aux[i+1])
            rota = copy.copy(aux)
    return rota

def inicializaMatrizesDistanciaTeste(conjEscolas, conjParadas, conjGaragens, conjOnibus):
    # Inicializar matrizes de distancias para o teste
    # Garagem 
    matrizDistancia = {}
    for escola in conjEscolas:
        matrizDistancia[escola] = 0.9
    for parada in conjParadas:
        if parada.identificador == 1:
            matrizDistancia[parada] = 1.1
        elif parada.identificador == 2:
            matrizDistancia[parada] = 1.2
        elif parada.identificador == 3:
            matrizDistancia[parada] = 2.6
        elif parada.identificador == 4:
            matrizDistancia[parada] = 2.2
        else:
            matrizDistancia[parada] = 3.2
    for garagem in conjGaragens:
        matrizDistancia[garagem] = 0.0
        garagem.matrizDistancia = matrizDistancia

    # Escola 
    matrizDistancia = {}
    for garagem in conjGaragens:
        matrizDistancia[garagem] = 0.9
    for parada in conjParadas:
        if parada.identificador == 1:
            matrizDistancia[parada] = 0.8
        elif parada.identificador == 2:
            matrizDistancia[parada] = 0.9
        elif parada.identificador == 3:
            matrizDistancia[parada] = 0.8
        elif parada.identificador == 4:
            matrizDistancia[parada] = 0.6
        else:
            matrizDistancia[parada] = 1.7
    for escola in conjEscolas:
        matrizDistancia[escola] = 0.0
        escola.matrizDistancia = matrizDistancia

    # Parada1 
    matrizDistanciaP1 = {}
    for garagem in conjGaragens:
        matrizDistanciaP1[garagem] = 1.1
    for escola in conjEscolas:
        matrizDistanciaP1[escola] = 0.8
    for parada in conjParadas:
        if parada.identificador == 1:
            matrizDistanciaP1[parada] = 0.0
        elif parada.identificador == 2:
            matrizDistanciaP1[parada] = 2.1
        elif parada.identificador == 3:
            matrizDistanciaP1[parada] = 2.5
        elif parada.identificador == 4:
            matrizDistanciaP1[parada] = 1.5
        else:
            matrizDistanciaP1[parada] = 1.9

    # Parada2
    matrizDistanciaP2 = {}
    for garagem in conjGaragens:
        matrizDistanciaP2[garagem] = 1.2
    for escola in conjEscolas:
        matrizDistanciaP2[escola] = 0.9
    for parada in conjParadas:
        if parada.identificador == 1:
            matrizDistanciaP2[parada] = 2.1
        elif parada.identificador == 2:
            matrizDistanciaP2[parada] = 0.0
        elif parada.identificador == 3:
            matrizDistanciaP2[parada] = 1.8
        elif parada.identificador == 4:
            matrizDistanciaP2[parada] = 1.9
        else:
            matrizDistanciaP2[parada] = 2.9

    # Parada3
    matrizDistanciaP3 = {}
    for garagem in conjGaragens:
        matrizDistanciaP3[garagem] = 2.6
    for escola in conjEscolas:
        matrizDistanciaP3[escola] = 0.8
    for parada in conjParadas:
        if parada.identificador == 1:
            matrizDistanciaP3[parada] = 2.5
        elif parada.identificador == 2:
            matrizDistanciaP3[parada] = 1.8
        elif parada.identificador == 3:
            matrizDistanciaP3[parada] = 0.0
        elif parada.identificador == 4:
            matrizDistanciaP3[parada] = 0.6
        else:
            matrizDistanciaP3[parada] = 2.2

    # Parada4
    matrizDistanciaP4 = {}
    for garagem in conjGaragens:
        matrizDistanciaP4[garagem] = 2.2
    for escola in conjEscolas:
        matrizDistanciaP4[escola] = 0.6
    for parada in conjParadas:
        if parada.identificador == 1:
            matrizDistanciaP4[parada] = 1.5
        elif parada.identificador == 2:
            matrizDistanciaP4[parada] = 1.9
        elif parada.identificador == 3:
            matrizDistanciaP4[parada] = 0.6
        elif parada.identificador == 4:
            matrizDistanciaP4[parada] = 0.0
        else:
            matrizDistanciaP4[parada] = 0.8

    # Parada5
    matrizDistanciaP5 = {}
    for garagem in conjGaragens:
        matrizDistanciaP5[garagem] = 3.2
    for escola in conjEscolas:
        matrizDistanciaP5[escola] = 1.7
    for parada in conjParadas:
        if parada.identificador == 1:
            matrizDistanciaP5[parada] = 1.9
        elif parada.identificador == 2:
            matrizDistanciaP5[parada] = 2.9
        elif parada.identificador == 3:
            matrizDistanciaP5[parada] = 2.2
        elif parada.identificador == 4:
            matrizDistanciaP5[parada] = 0.8
        else:
            matrizDistanciaP5[parada] = 0.0

    # Inicializa as matrizes de distancia das paradas
    for parada in conjParadas:
        if parada.identificador == 1:
            parada.matrizDistancia = matrizDistanciaP1
        elif parada.identificador == 2:
            parada.matrizDistancia = matrizDistanciaP2
        elif parada.identificador == 3:
            parada.matrizDistancia = matrizDistanciaP3
        elif parada.identificador == 4:
            parada.matrizDistancia = matrizDistanciaP4
        else:
            parada.matrizDistancia = matrizDistanciaP5



# A main que é o algoritmo de GRASP implementado para
if __name__ == '__main__' :
    # Inicializa os conjuntos de teste
    conjEscolas=[Escola()]
    conjParadas=[Paradatest(random.choice(conjEscolas), 1), Paradatest(random.choice(conjEscolas), 2), Paradatest(random.choice(conjEscolas), 3), Paradatest(random.choice(conjEscolas), 4), Paradatest(random.choice(conjEscolas), 5)]
    conjGaragens=[Garagem()] 
    conjOnibus= [Onibus(random.choice(conjGaragens))]
    #conjEstudantes=[]
    rota=[] #conjunto de rotas que inicia vazio 

    inicializaMatrizesDistanciaTeste(conjEscolas, conjParadas, conjGaragens, conjOnibus)
       

    # printConj(conjEscolas , 'escolas')
    # printConj(conjParadas, 'paradas')
    # printConj(conjGaragens, 'garagens')
    # printConj(conjOnibus, 'onibus')
    
    i=1
    while conjParadas :

        print ("************", i, "********")
        subRota = []
        parada = None
            
        if not rota or (onibus.horarioAtendimento > 0): 
            onibus = random.choice(conjOnibus) # pega um onibus aleatório no conj de onibus
            subRota.append(onibus.localAtual)
        else:
            # gerar nova rota pro mesmo busao
            subRota.append(onibus.localAtual)
    

        lrc = listaRestritaDeCandidatosInicial(0.1, onibus.localAtual, conjParadas)
        parada = random.choice(lrc)
        subRota.append(parada)
        onibus.escola = parada.escola # atualiza a escola para a qual o onibus ta fazendo rota
        onibus.lotacao += parada.qtAlunos # atualiza a lotação do onibus
        onibus.localAtual = parada # atualiza local do onibus
        conjParadas.remove(parada)

        # Organiza os horários do onibus
        onibus.horarioAtendimento -= distanciaTestes(onibus.localAtual, parada) # Modificar apos o teste de  distanciaTestes para distancia
        onibus.horarioAtendimento -= tempoEmbarque(parada.qtAlunos)
        onibus.tempoRota += tempoTrecho(distanciaTestes(onibus.localAtual, parada)) # Modificar apos o teste de  distanciaTestes para distancia
        onibus.tempoRota += tempoEmbarque(parada.qtAlunos)

        # Se o onibus ainda tiver capacidade
        while(onibus.capacidade > onibus.lotacao):
            lrc= listaRestritaDeCandidatosPorEscola(0.1, onibus.localAtual,conjParadas)
            if lrc != None:
                parada = random.choice(lrc)
                #Verifica se o horario de chegada do onibus e a capacidade vão permitir atender mais essa parada
                if (onibus.tempoRota+tempoDesembarque(onibus.lotacao)) <= onibus.escola.horarioInicioAulasMax  and (onibus.capacidade >= (onibus.lotacao + parada.qtAlunos)): #BUG não passa por essa condição
                    print ("condição A: add parada na subrota")
                    subRota.append(parada)
                    onibus.lotacao += parada.qtAlunos # atualiza a lotação do onibus
                    onibus.localAtual = parada # atualiza local de onibus
                    conjParadas.remove(parada)

                    # Organiza os horários do onibus
                    onibus.horarioAtendimento -= distanciaTestes(onibus.localAtual, parada) # Modificar apos o teste de  distanciaTestes para distancia
                    onibus.horarioAtendimento -= tempoEmbarque(parada.qtAlunos)
                    onibus.tempoRota += tempoTrecho(distanciaTestes(onibus.localAtual, parada)) # Modificar apos o teste de  distanciaTestes para distancia
                    onibus.tempoRota += tempoEmbarque(parada.qtAlunos)
                else:
                    print ("condição b: add escola na subrota")
                    onibus.horarioAtendimento -= tempoDesembarque(onibus.lotacao)
                    subRota.append(onibus.escola) # adiciona a escola como ultima parada da subRota
                    onibus.tempoRota += tempoTrecho(distanciaTestes(onibus.localAtual, onibus.escola)) # Modificar apos o teste de  distanciaTestes para distancia
                    onibus.tempoRota += tempoDesembarque(parada.qtAlunos)
                    onibus.localAtual = onibus.escola # atualiza local de onibus
                    break
            else:
                print ("condição c: add escola na subrota")
                onibus.horarioAtendimento -= tempoDesembarque(onibus.lotacao)
                subRota.append(onibus.escola) # adiciona a escola como ultima parada da subRota
                onibus.tempoRota += tempoTrecho(distanciaTestes(onibus.localAtual, onibus.escola)) # Modificar apos o teste de  distanciaTestes para distancia
                onibus.tempoRota += tempoDesembarque(parada.qtAlunos)
                onibus.localAtual = onibus.escola # atualiza local de onibus
                break
        
        printConj(subRota, "ANTES DO 2-OPT")    
        subRota = melhoriaDeRota(subRota)
        printConj(subRota, "DEPOIS DO 2-OPT") 
        rota.append(subRota)


    # printConj(conjEscolas, 'escolas')
    # printConj(conjGaragens, 'garagens')
    # printConj(conjOnibus, 'onibus')
    # for subrota in rota:
    #     printConj(subrota, 'rota')

    print(rota)
    

    
            

          
