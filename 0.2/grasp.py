# -*- coding: utf-8 -*-

import copy
import math
import random
from datetime import date, datetime, time, timedelta
from operator import itemgetter

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
        self.rotas=[]

    def distancia(self, localA, localB):
        # calcula a distancia rectliniar entre dois pontos
        x = abs(localA.latitude - localB.latitude) + abs(localA.longitude - localB.longitude)
        return x
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

    def criarLRC(self, fatorRandomizacao, matrizCustos ): # lista restrita de melhores candidatos
        # nessa função é onde realmente é criada a lista restrita de paradas 
        # candidatas a entrar na rota
        try:
            menorCusto= sorted(matrizCustos.values())[0]
            maiorCusto= sorted(matrizCustos.values())[len(matrizCustos)-1]
            grasp= menorCusto + fatorRandomizacao*(maiorCusto-menorCusto)
            lrc=[]
            for key in matrizCustos:
                if matrizCustos[key] <= grasp: # se o custo for menor ou igual que o valor de grasp
                    lrc.append(key) # Acrescenta a parada na LRC
            #print(matrizCustos)
            #print(lrc)
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
        matrizCustos= dict( sorted(matrizCustos.items(), key=itemgetter(1))) # Matriz de custos ordenada pelo menor custo
        return self.criarLRC(fatorRandomizacao, matrizCustos) 

    def listaRestritaDeCandidatosPorEscola(self, fatorRandomizacao, paradaAnterior):
        # Lista Restrita De Candidatos Por Escola
        # fatorRandomizacao = pode assumir valor entre 0 e 1 seve pra determinar o tamanho da lista LRC, onde se a =0 o metodo resá totalmente guloso e a= 1 totalmente aleatório
        matrizCustos={} # a estrutura de dados da matriz de custos é um diciionário onde a parada é a chave
        for parada in self.conjParadas:
            if parada.escola == paradaAnterior.escola:
                custo= self.distancia(paradaAnterior, parada) + self.distancia(parada, parada.escola)
                matrizCustos[ parada ]= custo
        matrizCustos= dict( sorted(matrizCustos.items(), key=itemgetter(1))) # Matriz de custos ordenada pelo menor custo
        return self.criarLRC(fatorRandomizacao, matrizCustos)

    def tempoTrecho(self, dist): 
        #tempo= (dist/29.333) # distancia em pes velocidade em pes/segundos gera o mesmo resultado q o calculo abaixo
        #print("1 tempo trecho: {} para a distancia de {} em pés".format(tempo,dist))
        dist = dist/5280.0 #transformando de pés para milhas
        tempo= (dist/20.0)*3600.0 # Tempo em segundos (mesmo usado por park)
        #print("2 tempo trecho: {} para a distancia de {} em milhas".format(tempo,dist))        
        return tempo

    def tempoEmbarque(self, qtAlunos): 
        tempo =float( 19.0 + 2.6 *qtAlunos) 
        #return (float)(tempo/60) # em minutos
        return tempo # em segundos

    def tempoDesembarque(self, qtAlunos): 
        tempo =float( 26.0 + 1.9 *qtAlunos)
        #return (float)(tempo/60) # em minutos
        return tempo # em segundos

    def tempoDaRota(self, rota):
        # somatória de tempo dos trechos, de embarques e desemarques de uma dada rota 
        tempo = 0.0
        paradaAnterior = None
        for parada in rota:
            if isinstance(parada,Parada):
                tempo += self.tempoEmbarque(parada.qtAlunos)
                tempo += self.tempoDesembarque(parada.qtAlunos)
            if paradaAnterior:
                #print('AQUI')
                tempo += self.tempoTrecho(self.distancia(paradaAnterior,parada)) 
                #print ("tempo: {}".format(tempo)) 
            paradaAnterior = parada
        return int(tempo)
            
    def melhoriaDeRota(self, rota): # algoritmo 2-opt
        # a primeira parada da rota é a garagem e portanto não deve poder trocar a ordem de visita da garagem com uma parada
        # assim como a ultima parada é a escola visitada
        for i in  range(1, len(rota)-(len(self.conjOnibusUteis[-1].escolas)+1)):
            aux = copy.copy(rota)
            temp = aux[i]
            aux[i] = aux[i+1]
            aux[i+1] = temp
            #print ("tempo aux :{} Tempo rota: {}".format(self.tempoDaRota(aux),self.tempoDaRota(rota)))
            if self.tempoDaRota(rota) > self.tempoDaRota(aux): # se trocando a ordem de visita entre duas paradas o caminho ficar menor eu troco a ordem das paradas
                #print("TROCOU  ", aux[i], aux[i+1])
                rota = copy.copy(aux)
            #print("tempo da rota:{}".format(self.tempoDaRota(rota)))
        return rota
    
    def somaSegundos(self, tempo, segundos):
        soma = datetime.combine(date(1,1,1), tempo) + timedelta(seconds=segundos)
        return soma.time()

    def subSegundos(self, tempo, segundos):
        soma = datetime.combine(date(1,1,1), tempo) - timedelta(seconds=segundos)
        return soma.time()

    def diferencaTempo(self, tempo1, tempo2):
        tempo1= datetime.combine(date(1,1,1), tempo1)
        tempo2= datetime.combine(date(1,1,1), tempo2)
        if tempo1  > tempo2:
            dif = tempo1-tempo2
        else:
            dif = tempo2-tempo1
        return dif.seconds #diferença do tempo em segundos

    def tempoRotaComEscolas(self,rota,escolas):
        rota = copy.copy(rota)
        rota.extend(escolas)
        return self.tempoDaRota(rota)

    def ajustaJanela(self, onibus):
        # Ajusta a janela de tempo do espediente do onibus de acordo com a janela de tempo da escola
        if onibus.fimEspediente < onibus.escolas[-1].horarioInicioAulasMin:
            print("11")
            onibus.inicioEspediente = self.somaSegundos(onibus.inicioEspediente, self.diferencaTempo(onibus.fimEspediente, onibus.escolas[-1].horarioInicioAulasMin))
            onibus.fimEspediente = self.somaSegundos(onibus.fimEspediente, self.diferencaTempo(onibus.fimEspediente, onibus.escolas[-1].horarioInicioAulasMin))
        elif onibus.fimEspediente > onibus.escolas[-1].horarioInicioAulasMax:
            print("22")
            onibus.inicioEspediente = self.subSegundos(onibus.inicioEspediente, self.diferencaTempo(onibus.fimEspediente, onibus.escolas[-1].horarioInicioAulasMax))
            onibus.fimEspediente = self.subSegundos(onibus.fimEspediente, self.diferencaTempo(onibus.fimEspediente, onibus.escolas[-1].horarioInicioAulasMax))

    def otimizaRotas (self):
        for onibus in self.conjOnibusUteis:
            self.ajustaJanela(onibus)
        for i in range(len(self.conjOnibusUteis)):
            
            print("############")
            print ("onibus: lot {}, Ti {}, Tf {}, escl {}".format(self.conjOnibusUteis[i].lotacao,self.conjOnibusUteis[i].inicioEspediente, self.conjOnibusUteis[i].fimEspediente, self.conjOnibusUteis[i].escolas[-1].id ))
            print("escola: inicio {} , fim {}".format(self.conjOnibusUteis[i].escolas[-1].horarioInicioAulasMin, self.conjOnibusUteis[i].escolas[-1].horarioInicioAulasMax))
            self.printConj(self.rotas[i], "SUB ROTA:{} ".format(i))

    def sbrpTestesPark(self,conjGaragens, conjOnibus, conjEscolas, conjParadas):# execulta os testes de tempo
        # Execulta com as instancias de Park
        # Faz análisas de tempo de execulsão

        # Insere os conjuntos de teste recebidos dos bancos de dados
        self.conjGaragens = conjGaragens # setar uma unica garagem num ponto médio entre as paradas
        self.conjOnibus = conjOnibus # setar 100 onibus com capacidade para 66 alunos
        self.conjEscolas = sorted(conjEscolas, key= Escola.get_horarioInicioAulasMin) # setar as RSRB de Park ( http://logistics.postech.ac.kr/Mixed_SBRP_Benchmark.html )
        self.conjParadas = conjParadas #setar as RSRB de Park ( http://logistics.postech.ac.kr/Mixed_SBRP_Benchmark.html )
        
        contEstourou=0
        
        i=1 # Um contador pra marcar as interações 

        while self.conjParadas:
            # Enquanto o conjunto de paradas não estiver vazio
            resultado = open('resultado.txt', 'w')
            print ("************", i, "********")
            
            subRota = [] # inicializo uma subrota
            parada = None

            # Cada sub rota inicializa com um novo onibus 
            onibus = random.choice(self.conjOnibus) # pega um onibus aleatório no conj de onibus
            self.conjOnibus.remove(onibus) # removo-o do conj de onibus 
            self.conjOnibusUteis.append(onibus) # acloco-o no conj de onibus utilizados
            subRota.append(onibus.localAtual) # inicializo a rota partindo da garagem
            # Ao final da contrução de sub rotas eu tento mesclar as rotas pra diminuir o numero de onibus nescessários

            '''
            # verifico se vou utilizar o mesmo onibus ou alocar um novo onibus para a próxima sub rota  
            if not self.rotas or onibus.fimEspediente >= conjEscolas[0].horarioInicioAulasMin: 
                # Verifica se é a primeira rota ou se o onibus não pode mais atenter a escola com menor o menor horário de estrada
                if self.rotas:
                    print("Novo   " + str(onibus.permissaoAtendimento))
                # Se tiver construindo a primeira subrota nenhum onibus estava alocado então seleciono um
                onibus = random.choice(self.conjOnibus) # pega um onibus aleatório no conj de onibus
                self.conjOnibus.remove(onibus) # removo-o do conj de onibus 
                self.conjOnibusUteis.append(onibus) # acloco-o no conj de onibus utilizados
                subRota.append(onibus.localAtual) # inicializo a rota partindo da garagem
            else:
                #print('orário bus:'+ str(onibus.permissaoAtendimento))
                # gerar nova rota pro mesmo busao
                print("Antigo   " + str(onibus.permissaoAtendimento))
                subRota.append(onibus.localAtual) # inicializo a rota partindo do ultimo local do onibus
                onibus.tempoRota=0.0 # limpa o tempo pra gerar uma nova rota
                onibus.lotacao= 0 # limpa a lotação do busão
            '''

            # inicializo uma sub rota
            lrc = self.listaRestritaDeCandidatosInicial(0.1, onibus.localAtual)
            parada = random.choice(lrc)
            subRota.append(parada)
            onibus.escolas.append(parada.escola) # atualiza as escolas para a qual o onibus ta fazendo rota
            onibus.escolas = list(set(onibus.escolas)) # retira repetições
            onibus.lotacao += parada.qtAlunos # atualiza a lotação do onibus
            self.conjParadas.remove(parada)

            # Organiza os horários do onibus
            onibus.tempoRota = self.tempoDaRota(subRota)
            onibus.fimEspediente = self.somaSegundos(onibus.fimEspediente,onibus.tempoRota)
            onibus.localAtual = parada # atualiza local do onibus

            # Se o onibus ainda tiver capacidade e o tempo da sub rota não estourou o tempo máximo
            if onibus.capacidade < onibus.lotacao:
                print("lotação ultrapassa capasidade")
            if self.tempoRotaComEscolas(subRota,onibus.escolas) < onibus.tempoMaxRota:
                print(" tempo da rota ultrapassa tempo maximo ")

            while(onibus.capacidade > onibus.lotacao):# and self.tempoRotaComEscolas(subRota,onibus.escolas) < onibus.tempoMaxRota):

                lrc= self.listaRestritaDeCandidatosPorEscola(0.1, onibus.localAtual)
                #print("1 LRC:{}".format(lrc))
                if lrc != None:
                    
                    parada = random.choice(lrc)
                    #print("Parada:{}".format(parada))

                    tempRota= onibus.tempoRota + self.tempoDesembarque(onibus.lotacao + parada.qtAlunos)+ self.tempoEmbarque(parada.qtAlunos) + self.tempoTrecho(self.distancia(onibus.localAtual, onibus.escolas[-1])) # tempo da rota incluindo essa parada
                    lotacaoBeP = onibus.lotacao + parada.qtAlunos # lotação do onibus após passar na parada nessa parada
                    #print("Tempo dessa rota com a parada:{} , inicio das aulas:{} , lotação do busão:{} , alunos na parada:{}".format(tempRota,onibus.escolas[-1].horarioInicioAulasMax,onibus.lotacao,parada.qtAlunos))

                    #Verifica se o horario de chegada na ultima escola e a capacidade vão permitir atender mais essa parada
                    if self.somaSegundos(onibus.fimEspediente,tempRota) < onibus.escolas[-1].horarioInicioAulasMax and lotacaoBeP <= onibus.capacidade: 
                        # adiciona uma parada na sub rota e a retira do conjunto de paradas
                        #print ("condição A: add parada na subrota")
                        subRota.append(parada)
                        onibus.lotacao += parada.qtAlunos # atualiza a lotação do onibus
                        onibus.localAtual = parada # atualiza local de onibus
                        self.conjParadas.remove(parada)

                        # Organiza os horários do onibus
                        onibus.tempoRota = self.tempoDaRota(subRota)
                    else:
                        #print ("condição b: add escola na subrota se não tiver tempo ou capacidade")
                        '''
                        if not self.somaSegundos(onibus.fimEspediente,tempRota) < onibus.escolas[-1].horarioInicioAulasMax:
                            print("foi tempo")
                        if not lotacaoBeP <= onibus.capacidade:
                            print("foi capacidade") 
                        '''   
                        subRota.append(onibus.escolas[-1]) # adiciona a escola como ultima parada da subRota
                        onibus.tempoRota = self.tempoDaRota(subRota)
                        onibus.localAtual = onibus.escolas[-1] # atualiza local de onibus
                        break
                else:
                    #print ("condição c: add escola na subrota se não tiver ais paradas na lrc")
                    subRota.append(onibus.escolas[-1]) # adiciona a escola como ultima parada da subRota
                    onibus.tempoRota = self.tempoDaRota(subRota)
                    onibus.localAtual = onibus.escolas[-1] # atualiza local de onibus
                    break
            
            if not isinstance(subRota[-1],Escola):
                #print("Eita! faltou parar na escola.")
                subRota.append(onibus.escolas[-1]) # adiciona as escolas como ultimas paradas da subRota
                onibus.tempoRota += self.tempoTrecho(self.distancia(onibus.localAtual, onibus.escolas[-1])) 
                onibus.tempoRota += self.tempoDesembarque(parada.qtAlunos)
                onibus.localAtual = onibus.escolas[-1] # atualiza local de onibus
             
            
            
            subRota = self.melhoriaDeRota(subRota) # Aplica melhoria na sub rota

            onibus.fimEspediente = self.somaSegundos(onibus.fimEspediente, self.tempoDaRota(subRota)) # Soma ao expediente do onibuso tempo dessa sub rota
            #print("fim espediente bus {}".format(onibus.fimEspediente))
            # Atualiza a permissão de atender mais rotas do onibus
            
       
            # Incluia sub rota no conj de rotas
            self.rotas.append(subRota)
     
            # Prints
            #self.printConj(subRota, "SUB ROTA:{} ".format(i))
             
            if self.tempoDaRota(subRota) > 2700:
                contEstourou +=1

            print(self.tempoDaRota(subRota))
            #print("Onibus utilizados= {}".format(len(self.conjOnibusUteis)))
            
            i+=1
            

        # otimizar rotas
        self.otimizaRotas()



        # printConj(conjEscolas, 'escolas')
        # printConj(conjGaragens, 'garagens')
        # printConj(conjOnibus, 'onibus')
        print("{} estouraram".format(contEstourou))

        '''
        for subrota in self.rotas:
            self.printConj(subrota, 'rota')

        #print(self.rotas)
        resultado.close()
        '''

    def sbrpComercial(conjGaragens, conjOnibus, conjEstudantes, conjEscolas,conjParadas):# Não funciona ainda
        # Versão de uso

        # execulta o programa considerando 
        # a API maps da google que já retorna a distancia entre
        #  dois pontos com tempo de rota

        # Insere os conjuntos de teste
        self.conjGaragens = conjGaragens
        self.conjOnibus = conjOnibus
        self.conjEstudantes = conjEstudantes
        self.conjEscolas = conjEscolas
        self.conjParadas = conjParadas

        #self.inicializaMatrizesDistancia() # Chama a API do Google


        