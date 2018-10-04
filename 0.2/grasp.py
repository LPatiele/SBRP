# -*- coding: utf-8 -*-

import copy
import math
import random
from datetime import time

from models import Escola, Estudante, Garagem, Onibus, Parada



class Grasp:

    def __init__(self, *args, **kwargs):
        #inicializa todos os conjuntos vazios
        self.conjEscolas=[]
        self.conjParadas=[]
        self.conjGaragens=[] 
        self.conjOnibus= []
        self.conjEstudantes=[]
        self.conjOnibusUteis=[]
        self.rotaFinal=[]

    def distancia(self, localA, localB):
        # calcula a distancia euclidiana entre dois pontos
        x= (localA.latitude - localB.latitude)**2 +(localA.longitude - localB.longitude)**2
        return math.sqrt(x)
        '''
        # calcula distancia entre coordenadas geograficas
        dla = float(((localA.latitude - localB.latitude)/60)*1852) #diferença entre as latitudes em metros
        dlo =  float(((localA.longitude - localB.longitude)/60)*1852 )#diferença entre as longitudes em metros
        return float(math.sqrt(dla**2 + dlo**2)) #distancia em metros 
        '''

    def printConj(self,conj, nome): # imprime na tela os conjuntos definidos ex: escolas, garagens, paradas,etc.
        print("Conjunto de ", nome)
        for i in conj:
            print(i)

    def criarLRC(self, fatorRandomizacao, matrizCustos ): # lista restrita de candidatos
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
    
    def listaRestritaDeCandidatosInicial(self, fatorRandomizacao, localSaidaOnibus): 
        # Lista Restrita De Candidatos Inicial
        # fatorRandomizacao = pode assumir valor entre 0 e 1 seve pra determinar o tamanho da lista LRC, onde se a =0 o metodo resá totalmente guloso e a= 1 totalmente aleatório
        matrizCustos={} # a estrutura de dados da matriz de custos é um diciionário onde a parada é a chave
        for parada in self.conjParadas:
            custo= self.distancia(localSaidaOnibus, parada) + self.distancia(parada, parada.escola)
            matrizCustos[ parada ] = custo
        return self.criarLRC(fatorRandomizacao, matrizCustos) 

    def listaRestritaDeCandidatosPorEscola(self, fatorRandomizacao, paradaAnterior):
        # Lista Restrita De Candidatos Por Escola
        # fatorRandomizacao = pode assumir valor entre 0 e 1 seve pra determinar o tamanho da lista LRC, onde se a =0 o metodo resá totalmente guloso e a= 1 totalmente aleatório
        matrizCustos={} # a estrutura de dados da matriz de custos é um diciionário onde a parada é a chave
        for parada in self.conjParadas:
            if parada.escola == paradaAnterior.escola:
                custo= self.distancia(paradaAnterior, parada) + self.distancia(parada, parada.escola)
                matrizCustos[ parada ]= custo
        return self.criarLRC(fatorRandomizacao, matrizCustos)

    def tempoTrecho(self, dist): 
        tempo = (float)(dist/8.8888888889) # t=s/v , sendo s em metros e v em m/s e t em segundos
        #return (float)(tempo/60.0) # em minutos
        return tempo # em segundos

    def tempoEmbarque(self, qtAlunos): 
        tempo =(float)( 1.9 + 2.6 *qtAlunos) 
        #return (float)(tempo/60) # em minutos
        return tempo # em segundos

    def tempoDesembarque(self, qtAlunos): 
        tempo =(float)( 2.6 + 1.9 *qtAlunos)
        #return (float)(tempo/60) # em minutos
        return tempo # em segundos

    def tempoDaRota(self, rota):
        # somatória de tempo dos trechos, de embarques e desemarques de uma dada rota 
        tempo = 0.0
        paradaAnterior = None
        for parada in rota:
            if str(parada.__class__) == "models.Parada":
                if paradaAnterior:
                    tempo += self.tempoTrecho(self.distancia(paradaAnterior,parada))
                    tempo += self.tempoEmbarque(parada.qtAlunos)
                    tempo += self.tempoDesembarque(parada.qtAlunos)
                paradaAnterior = parada
        return tempo
            
    def melhoriaDeRota(self, rota): # algoritmo 2-opt
        # a primeira parada da rota é a garagem e portanto não deve poder trocar a ordem de visita da garagem com uma parada
        # assim como a ultima parada é a escola visitada
        for i in  range(1, len(rota)-2):
            aux = copy.copy(rota)
            temp = aux[i]
            aux[i] = aux[i+1]
            aux[i+1] = temp
            #print ("tempo aux :{} Tempo rota: {}".format(self.tempoDaRota(aux),self.tempoDaRota(rota)))
            if self.tempoDaRota(rota) > self.tempoDaRota(aux): # se trocando a ordem de visita entre duas paradas o caminho ficar menor eu troco a ordem das paradas
                print("TROCOU  ", aux[i], aux[i+1])
                rota = copy.copy(aux)
            print("tempo da rota:{}".format(self.tempoDaRota(rota)))
        return rota
    
    def sbrpTestesPark(self,conjGaragens, conjOnibus, conjEscolas, conjParadas):# execulta os testes de tempo
        # Execulta com as instancias de Park
        # Faz análisas de tempo de execulsão

        # Insere os conjuntos de teste recebidos dos bancos de dados
        self.conjGaragens = conjGaragens # setar uma unica garagem num ponto médio entre as paradas
        self.conjOnibus = conjOnibus # setar 100 onibus com capacidade para 66 alunos
        self.conjEscolas = conjEscolas # setar as RSRB de Park ( http://logistics.postech.ac.kr/Mixed_SBRP_Benchmark.html )
        self.conjParadas = conjParadas #setar as RSRB de Park ( http://logistics.postech.ac.kr/Mixed_SBRP_Benchmark.html )
        
        
        i=1
        onibus= None
        while self.conjParadas: # BUG só esta tirando uma parada por vez PQ????????
            # Enquanto o conjunto de paradas não estiver vazio e tiver onibus disponiveis

            print ("************", i, "********")
            
            subRota = [] # inicializo uma subrota
            parada = None
                
            if not self.rotaFinal or (onibus.horarioAtendimento > 0): 
                # Se não tiver subrota nenhuma ou o ultimo onibus não estiver em horário de atendimento
                onibus = random.choice(self.conjOnibus) # pega um onibus aleatório no conj de onibus
                self.conjOnibus.remove(onibus)
                self.conjOnibusUteis.append(onibus)
                subRota.append(onibus.localAtual)
            else:
                # gerar nova rota pro mesmo busao
                subRota.append(onibus.localAtual)
                onibus.tempoRota=0.0 # limpa o tempo pra gerar uma nova rota
                onibus.lotacao= 0 # limpa a lotação do busão
        

            lrc = self.listaRestritaDeCandidatosInicial(0.1, onibus.localAtual)
            # Colocar um while aqui pra cotinuar procurando uma parada aceitavel 
            # enquanto não encontrar uma parada que o horário e a capacidade do onibus permita 
            # ser atendida ou enquanto tiver paradas na lcr
            parada = random.choice(lrc)
            subRota.append(parada)
            onibus.escola.append(parada.escola) # atualiza as escolas para a qual o onibus ta fazendo rota
            onibus.lotacao += parada.qtAlunos # atualiza a lotação do onibus
            self.conjParadas.remove(parada)

            # Organiza os horários do onibus
            onibus.tempoRota += self.tempoTrecho(self.distancia(onibus.localAtual, parada)) 
            onibus.tempoRota += self.tempoEmbarque(parada.qtAlunos)
            onibus.horarioAtendimento -= onibus.tempoRota
            onibus.localAtual = parada # atualiza local do onibus

            # Se o onibus ainda tiver capacidade
            while(onibus.capacidade > onibus.lotacao):
                lrc= self.listaRestritaDeCandidatosPorEscola(0.1, onibus.localAtual)
                if lrc != None:
                    parada = random.choice(lrc)
                
                    tempRota= onibus.tempoRota + self.tempoDesembarque(onibus.lotacao) + self.tempoTrecho(self.distancia(onibus.localAtual, onibus.escola[-1])) # tempo da rota incluindo essa parada
                    lotacaoBeP = onibus.lotacao + parada.qtAlunos # lotação do onibus após passar na parada nessa parada
                    print("Tempo dessa rota com a parada:{} , inicio das aulas:{} , lotação do busão:{} , alunos na parada:{}".format(tempRota,onibus.escola[-1].horarioInicioAulasMax,onibus.lotacao,parada.qtAlunos))

                    #Verifica se o horario de chegada na escola e a capacidade vão permitir atender mais essa parada
                    if tempRota <= onibus.escola[-1].horarioInicioAulasMax and lotacaoBeP <= onibus.capacidade  and (onibus.horarioAtendimento - tempRota) > 0:
                        # adiciona uma parada na sub rota e a retira do conjunto de paradas
                        print ("condição A: add parada na subrota")
                        subRota.append(parada)
                        onibus.lotacao += parada.qtAlunos # atualiza a lotação do onibus
                        onibus.localAtual = parada # atualiza local de onibus
                        self.conjParadas.remove(parada)

                        # Organiza os horários do onibus
                        onibus.horarioAtendimento -= self.tempoEmbarque(parada.qtAlunos) + self.tempoTrecho(self.distancia(onibus.localAtual, onibus.escola[-1])) 
                        onibus.tempoRota += self.tempoTrecho(self.distancia(onibus.localAtual, parada)) 
                        onibus.tempoRota += self.tempoEmbarque(parada.qtAlunos)
                    else:
                        print ("condição b: add escola na subrota se não tiver tempo ou capacidade")
                        onibus.horarioAtendimento -= self.tempoDesembarque(onibus.lotacao) + self.tempoTrecho(self.distancia(onibus.localAtual, onibus.escola[-1])) 
                        subRota.append(onibus.escola[-1]) # adiciona a escola como ultima parada da subRota
                        onibus.tempoRota += self.tempoTrecho(self.distancia(onibus.localAtual, onibus.escola[-1])) 
                        onibus.tempoRota += self.tempoDesembarque(parada.qtAlunos)
                        onibus.localAtual = onibus.escola[-1] # atualiza local de onibus
                        break
                else:
                    print ("condição c: add escola na subrota se não tiver ais paradas na lrc")
                    onibus.horarioAtendimento -= self.tempoDesembarque(onibus.lotacao) + self.tempoTrecho(self.distancia(onibus.localAtual, onibus.escola[-1])) 
                    subRota.append(onibus.escola[-1]) # adiciona a escola como ultima parada da subRota
                    onibus.tempoRota += self.tempoTrecho(self.distancia(onibus.localAtual, onibus.escola[-1])) 
                    onibus.tempoRota += self.tempoDesembarque(parada.qtAlunos)
                    onibus.localAtual = onibus.escola[-1] # atualiza local de onibus
                    break

            if str(subRota[-1].__class__) != "models.Escola":
                print("Eita! faltou parar na escola.")
                onibus.horarioAtendimento -= self.tempoDesembarque(onibus.lotacao)+self.tempoTrecho(self.distancia(onibus.localAtual, onibus.escola[-1])) 
                subRota.append(onibus.escola[-1]) # adiciona a escola como ultima parada da subRota
                onibus.tempoRota += self.tempoTrecho(self.distancia(onibus.localAtual, onibus.escola[-1])) 
                onibus.tempoRota += self.tempoDesembarque(parada.qtAlunos)
                onibus.localAtual = onibus.escola[-1] # atualiza local de onibus
               
            subRota = self.melhoriaDeRota(subRota)
            self.printConj(subRota, "SUB ROTA:{} ".format(i)) 
            self.rotaFinal.append(subRota)
            print("Onibus utilizados= {}".format(len(self.conjOnibusUteis)))
            i+=1


        # printConj(conjEscolas, 'escolas')
        # printConj(conjGaragens, 'garagens')
        # printConj(conjOnibus, 'onibus')
        # for subrota in rota:
        #     printConj(subrota, 'rota')

        #print(self.rotaFinal)

    def sbrpComercial(conjGaragens, conjOnibus, conjEstudantes, conjEscolas,conjParadas):# Não funciona ainda
        # Versão de uso

        # execulta o programa considerando matrizes de distancia 
        # e não pontos de geolocalização eu fiz desse modo pra usar 
        # a API maps da google que já retorna a distancia entre
        #  dois pontos com tempo de rota

        # Insere os conjuntos de teste
        self.conjGaragens = conjGaragens
        self.conjOnibus = conjOnibus
        self.conjEstudantes = conjEstudantes
        self.conjEscolas = conjEscolas
        self.conjParadas = conjParadas

        #self.inicializaMatrizesDistancia() # Chama a API do Google


        # printConj(conjEscolas , 'escolas')
        # printConj(conjParadas, 'paradas')
        # printConj(conjGaragens, 'garagens')
        # printConj(conjOnibus, 'onibus')
        
        i=1
        while self.conjParadas :

            print ("************", i, "********")
            subRota = []
            parada = None
                
            if not rota or (onibus.horarioAtendimento > 0): 
                onibus = random.choice(conjOnibus) # pega um onibus aleatório no conj de onibus
                subRota.append(onibus.localAtual)
            else:
                # gerar nova rota pro mesmo busao
                subRota.append(onibus.localAtual)
        

            lrc = self.listaRestritaDeCandidatosInicial(0.1, onibus.localAtual)
            parada = random.choice(lrc)
            subRota.append(parada)
            onibus.escola = parada.escola # atualiza a escola para a qual o onibus ta fazendo rota
            onibus.lotacao += parada.qtAlunos # atualiza a lotação do onibus
            onibus.localAtual = parada # atualiza local do onibus
            self.conjParadas.remove(parada)

            # Organiza os horários do onibus
            onibus.horarioAtendimento -= self.distancia(onibus.localAtual, parada)
            onibus.horarioAtendimento -= self.tempoEmbarque(parada.qtAlunos)
            onibus.tempoRota += self.tempoTrecho(self.distancia(onibus.localAtual, parada)) 
            onibus.tempoRota += self.tempoEmbarque(parada.qtAlunos)

            # Se o onibus ainda tiver capacidade
            while(onibus.capacidade > onibus.lotacao):
                lrc= self.listaRestritaDeCandidatosPorEscola(0.1, onibus.localAtual)
                if lrc != None:
                    parada = random.choice(lrc)
                    #Verifica se o horario de chegada do onibus e a capacidade vão permitir atender mais essa parada
                    if (onibus.tempoRota+self.tempoDesembarque(onibus.lotacao)) <= onibus.escola.horarioInicioAulasMax  and (onibus.capacidade >= (onibus.lotacao + parada.qtAlunos)): #BUG não passa por essa condição
                        print ("condição A: add parada na subrota")
                        subRota.append(parada)
                        onibus.lotacao += parada.qtAlunos # atualiza a lotação do onibus
                        onibus.localAtual = parada # atualiza local de onibus
                        self.conjParadas.remove(parada)

                        # Organiza os horários do onibus
                        onibus.horarioAtendimento -= self.distancia(onibus.localAtual, parada) 
                        onibus.horarioAtendimento -= self.tempoEmbarque(parada.qtAlunos)
                        onibus.tempoRota += self.tempoTrecho(self.distancia(onibus.localAtual, parada)) 
                        onibus.tempoRota += self.tempoEmbarque(parada.qtAlunos)
                    else:
                        print ("condição b: add escola na subrota")
                        onibus.horarioAtendimento -= self.tempoDesembarque(onibus.lotacao)
                        subRota.append(onibus.escola) # adiciona a escola como ultima parada da subRota
                        onibus.tempoRota += self.tempoTrecho(self.distancia(onibus.localAtual, onibus.escola)) 
                        onibus.tempoRota += self.tempoDesembarque(parada.qtAlunos)
                        onibus.localAtual = onibus.escola # atualiza local de onibus
                        break
                else:
                    print ("condição c: add escola na subrota")
                    onibus.horarioAtendimento -= self.tempoDesembarque(onibus.lotacao)
                    subRota.append(onibus.escola) # adiciona a escola como ultima parada da subRota
                    onibus.tempoRota += self.empoTrecho(self.distancia(onibus.localAtual, onibus.escola)) 
                    onibus.tempoRota += self.tempoDesembarque(parada.qtAlunos)
                    onibus.localAtual = onibus.escola # atualiza local de onibus
                    break
            
            self.printConj(subRota, "ANTES DO 2-OPT")    
            subRota = melhoriaDeRota(subRota)
            self.printConj(subRota, "DEPOIS DO 2-OPT")
            
            
            rotaFinal.append(subRota)


        # printConj(conjEscolas, 'escolas')
        # printConj(conjGaragens, 'garagens')
        # printConj(conjOnibus, 'onibus')
        # for subrota in rota:
        #     printConj(subrota, 'rota')

        print(self.rota)
    