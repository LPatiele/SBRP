# -*- coding: utf-8 -*-
from datetime import time
import random
import math

from onibus import Onibus
from escola import Escola
from parada import Parada
from garagem import Garagem
from estudante import Estudante


def distancia(localA, localB):# calcula distancia entre coordenadas geograficas
    dla = (float)(((localA.latitude - localB.latitude)/60)*1852) #diferença entre as latitudes em metros
    dlo =  (float)(((localA.longitude - localB.longitude)/60)*1852 )#diferença entre as longitudes em metros
    return math.sqrt(dla**2 + dlo**2) #distancia em metros 

def printConj(conj):
    print("Conjunto de ", type(conj[0]))
    for i in conj:
        print(i)

def criarLRC(fatorRandomizacao, matrizCustos ): # nessa função é onde realmente é criada a lista restrita de paradas candidatas a entrar na rota
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
        

def listaRestritaDeCandidatosInicial(fatorRandomizacao, localSaidaOnibus, conjParadas): #LRCi
    # fatorRandomizacao = pode assumir valor entre 0 e 1 seve pra determinar o tamanho da lista LRC, onde se a =0 o metodo resá totalmente guloso e a= 1 totalmente aleatório
    matrizCustos={} # a estrutura de dados da matriz de custos é um diciionário onde a parada é a chave
    for parada in conjParadas:
        custo= distancia(localSaidaOnibus, parada) + distancia(parada, parada.escola)
        matrizCustos[ parada ]= custo
    return criarLRC(fatorRandomizacao, matrizCustos)

def listaRestritaDeCandidatosPorEscola(fatorRandomizacao, paradaAnterior, conjParadas): #LRCj
    # fatorRandomizacao = pode assumir valor entre 0 e 1 seve pra determinar o tamanho da lista LRC, onde se a =0 o metodo resá totalmente guloso e a= 1 totalmente aleatório
    matrizCustos={} # a estrutura de dados da matriz de custos é um diciionário onde a parada é a chave
    for parada in conjParadas:
        if parada.escola == paradaAnterior.escola:
            custo= distancia(paradaAnterior, parada) + distancia(parada, parada.escola)
            matrizCustos[ parada ]= custo
    return criarLRC(fatorRandomizacao, matrizCustos)

def tempoTrecho(distancia): # em minutos
    tempo = (float)(distancia/8.8888888889) # t=s/v , sendo s em metros e v em m/s e t em segundos
    return (float)(tempo/60.0)

def tempoEmbarque(qtAlunos): # em minutos
    tempo =(float)( 1.9 + 2.6 *qtAlunos) #em segundos
    return (float)(tempo/60)

    
def tempoDesembarque(qtAlunos): # em minutos
    tempo =(float)( 2.6 + 1.9 *qtAlunos) #em segundos
    return (float)(tempo/60)

if __name__ == '__main__' :
    # Inicializa os conjuntos
    conjEscolas=[Escola(), Escola()]
    conjParadas=[Parada(random.choice(conjEscolas)), Parada(random.choice(conjEscolas)), Parada(random.choice(conjEscolas)), Parada(random.choice(conjEscolas)), Parada(random.choice(conjEscolas)), Parada(random.choice(conjEscolas)), Parada(random.choice(conjEscolas)) ]
    conjGaragens=[Garagem(), Garagem() ] 
    conjOnibus= [Onibus(random.choice(conjGaragens)), Onibus(random.choice(conjGaragens)), Onibus(random.choice(conjGaragens)), Onibus(random.choice(conjGaragens)), Onibus(random.choice(conjGaragens))]
    #conjEstudantes=[]
    rota=[] #conjunto de rotas que inicia vazio 

    printConj(conjEscolas)
    printConj(conjParadas)
    printConj(conjGaragens)
    printConj(conjOnibus)
    

    while conjParadas :
        subRota = []
        parada = None
            
        if not rota or (onibus.horarioAtendimento > 0):
            onibus= random.choice(conjOnibus) # pega um onibus aleatório no conj de onibus
        else:
            # gerar nova rota pro mesmo busao
            subRota = onibus.localAtual
    

        lrc = listaRestritaDeCandidatosInicial(0.1, onibus.localAtual, conjParadas)
        parada = random.choice(lrc)
        subRota.append(parada)
        onibus.escola = parada.escola # atualiza a escola para a qual o onibus ta fazendo rota
        onibus.lotacao += parada.qtAlunos # atualiza a lotação do onibus
        onibus.localAtual = parada # atualiza local do onibus
        conjParadas.remove(parada)

        # Organiza os horários do onibus
        onibus.horarioAtendimento -= distancia(onibus.localAtual, parada)
        onibus.horarioAtendimento -= tempoEmbarque(parada.qtAlunos)
        onibus.tempoRota += distancia(onibus.localAtual, parada)
        onibus.tempoRota += tempoEmbarque(parada.qtAlunos)

        # Se o onibus ainda tiver capacidade
        while(onibus.capacidade > onibus.lotacao):
            lrc= listaRestritaDeCandidatosPorEscola(0.1, onibus.localAtual,conjParadas)
            if lrc != None:
                parada = random.choice(lrc)
                #Verifica se o horario de chegada do onibus e a capacidade vão permitir atender mais essa parada
                if (onibus.tempoRota+tempoDesembarque(onibus.lotacao)) > onibus.escola.horarioInicioAulasMax  and (onibus.capacidade > (onibus.lotacao + parada.qtAlunos)) :
                    subRota.append(parada)
                    onibus.lotacao += parada.qtAlunos # atualiza a lotação do onibus
                    onibus.localAtual = parada # atualiza local de onibus
                    conjParadas.remove(parada)

                    # Organiza os horários do onibus
                    onibus.horarioAtendimento -= distancia(onibus.localAtual, parada)
                    onibus.horarioAtendimento -= tempoEmbarque(parada.qtAlunos)
                    onibus.tempoRota += distancia(onibus.localAtual, parada)
                    onibus.tempoRota += tempoEmbarque(parada.qtAlunos)
                else:
                    onibus.horarioAtendimento -= tempoDesembarque(onibus.lotacao)
                    subRota.append(onibus.escola) # adiciona a escola como ultima parada da subRota
                    onibus.tempoRota += distancia(onibus.localAtual, onibus.escola)
                    onibus.tempoRota += tempoDesembarque(parada.qtAlunos)
                    onibus.localAtual = onibus.escola # atualiza local de onibus
                    break
                    
                    

            else:
                onibus.horarioAtendimento -= tempoDesembarque(onibus.lotacao)
                subRota.append(onibus.escola) # adiciona a escola como ultima parada da subRota
                onibus.tempoRota += distancia(onibus.localAtual, onibus.escola)
                onibus.tempoRota += tempoDesembarque(parada.qtAlunos)
                onibus.localAtual = onibus.escola # atualiza local de onibus
                break
        
        rota.append(subRota)


    printConj(conjEscolas)
    printConj(conjGaragens)
    printConj(conjOnibus)

    print(rota)
    
            

          
