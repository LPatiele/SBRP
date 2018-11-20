# -*- coding: utf-8 -*-

import copy
import math
import random
from datetime import date, datetime, time, timedelta
from operator import itemgetter
from os import remove

from models import Escola, Garagem, Onibus, Parada,Rota


class GraspML:

    def __init__(self, *args, **kwargs):
        #inicializa todos os conjuntos vazios
        self.conjEscolas=[]
        self.conjParadas=[]
        self.conjGaragens=[] 
        self.conjOnibus= []
        self.conjOnibusUteis=[]
        self.rotas=[] # para cada rota é designado um onibus distinto
        self.miniRotas={} # dicionário chave=onibus e valor=rota do onibus

    def distancia(self, localA, localB): 
        # calcula a distancia rectliniar entre dois pontos
        x = abs(localA.latitude - localB.latitude) + abs(localA.longitude - localB.longitude)
        return x

    def printConj(self,conj, nome): # imprime na tela os conjuntos definidos ex: escolas, garagens, paradas,etc.
        #print(str(nome))
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
    
    def listaRestritaDeCandidatosInicial(self, fatorRandomizacao, localSaidaOnibus, grupo): 
        # Lista Restrita De Candidatos Inicial
        # fatorRandomizacao = pode assumir valor entre 0 e 1 seve pra determinar o tamanho da lista LRC, onde se a =0 o metodo resá totalmente guloso e a= 1 totalmente aleatório
        matrizCustos={} # a estrutura de dados da matriz de custos é um diciionário onde a parada é a chave
        for parada in grupo:
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
        #tempo= (dist/29.333) # distancia em pes e velocidade em pes/segundos gera o mesmo resultado q o calculo abaixo
        dist = dist/5280.0 #transformando de pés para milhas
        tempo= (dist/20.0)*3600.0 # Tempo em segundos (mesmo usado por park)
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
                #tempo += self.tempoDesembarque(parada.qtAlunos)
            if paradaAnterior:
                #print('AQUI')
                tempo += self.tempoTrecho(self.distancia(paradaAnterior,parada)) 
                #print ("tempo: {}".format(tempo)) 
            paradaAnterior = parada
        return int(tempo)
            
    def melhoriaDeRota(self, rota): # algoritmo 2-opt
        # a primeira parada da rota é a garagem e portanto não deve poder trocar a ordem de visita da garagem com uma parada
        # assim como sa ultimas paradas são as escolas visitadas
        for i in  range(2, len(rota)-len(self.conjOnibusUteis[-1].escolas)):
            aux = copy.copy(rota)
            temp = aux[i]
            aux[i] = aux[i-1]
            aux[i-1] = temp
            #print ("tempo aux :{} Tempo rota: {}".format(self.tempoDaRota(aux),self.tempoDaRota(rota)))
            if self.tempoDaRota(rota) > self.tempoDaRota(aux): # se trocando a ordem de visita entre duas paradas o caminho ficar menor eu troco a ordem das paradas
                #print("TROCOU  ", aux[i], aux[i-1])
                rota = copy.copy(aux)
            #print("tempo da rota:{}".format(self.tempoDaRota(rota)))
        return rota
    
    def somaSegundos(self, tempo, segundos): # soma segundos à um horário
        soma = datetime.combine(date(1,1,1), tempo) + timedelta(seconds=segundos)
        return soma.time()

    def subSegundos(self, tempo, segundos): # subtrai segundos de um horário
        sub = datetime.combine(date(1,1,1), tempo) - timedelta(seconds=segundos)
        return sub.time()

    def diferencaTempo(self, tempo1, tempo2): # calcula a diferença de tempo entre dois horários
        tempo1= datetime.combine(date(1,1,1), tempo1)
        tempo2= datetime.combine(date(1,1,1), tempo2)
        if tempo1  > tempo2:
            dif = tempo1-tempo2
        else:
            dif = tempo2-tempo1
        return dif.seconds #diferença do tempo em segundos

    def tempoRotaComCarga_(self,rota): #conta o tempo da rota em que há alunos no onibus
        aux = copy.copy(rota)
        # retorna o tempo da rota desconsiderando a viagem vazia da garagem à primeira parada
        return self.tempoDaRota(aux) - self.tempoTrecho(self.distancia(aux[0],aux[1]))

    def ajustaJanela(self): # ajusta os horários do onibus pra respeitar a janela de tempo da escola
        # Ajusta a janela de tempo do espediente do onibus de acordo com a janela de tempo da escola
        for onibus in self.conjOnibusUteis:
            if onibus.fimEspediente < onibus.escolas[-1].horarioInicioAulasMin:
                
                onibus.inicioEspediente = self.somaSegundos(onibus.inicioEspediente, self.diferencaTempo(onibus.fimEspediente, onibus.escolas[-1].horarioInicioAulasMin))
                onibus.fimEspediente = self.somaSegundos(onibus.fimEspediente, self.diferencaTempo(onibus.fimEspediente, onibus.escolas[-1].horarioInicioAulasMin))
            elif onibus.fimEspediente > onibus.escolas[-1].horarioInicioAulasMax:
                
                onibus.inicioEspediente = self.subSegundos(onibus.inicioEspediente, self.diferencaTempo(onibus.fimEspediente, onibus.escolas[-1].horarioInicioAulasMax))
                onibus.fimEspediente = self.subSegundos(onibus.fimEspediente, self.diferencaTempo(onibus.fimEspediente, onibus.escolas[-1].horarioInicioAulasMax))

    def ajustaJanela_(self,onibus): # ajusta os horários do onibus pra respeitar a janela de tempo da escola
        # Ajusta a janela de tempo do espediente do onibus de acordo com a janela de tempo da escola
        if onibus.fimEspediente < onibus.escolas[-1].horarioInicioAulasMin:
            onibus.inicioEspediente = self.somaSegundos(onibus.inicioEspediente, self.diferencaTempo(onibus.fimEspediente, onibus.escolas[-1].horarioInicioAulasMin))
            onibus.fimEspediente = self.somaSegundos(onibus.fimEspediente, self.diferencaTempo(onibus.fimEspediente, onibus.escolas[-1].horarioInicioAulasMin))
        elif onibus.fimEspediente > onibus.escolas[-1].horarioInicioAulasMax:
            onibus.inicioEspediente = self.subSegundos(onibus.inicioEspediente, self.diferencaTempo(onibus.fimEspediente, onibus.escolas[-1].horarioInicioAulasMax))
            onibus.fimEspediente = self.subSegundos(onibus.fimEspediente, self.diferencaTempo(onibus.fimEspediente, onibus.escolas[-1].horarioInicioAulasMax))

    def printMiniRotas(self):
        for onibus in self.conjOnibusUteis:
            print("______________________________________________________________________________")
            print ("onibus: lot {}, Ti {}, Tf {}, escl {}".format(onibus.lotacao,onibus.inicioEspediente, onibus.fimEspediente, onibus.escolas[-1].id ))
            print("escola: inicio {} , fim {}".format(onibus.escolas[-1].horarioInicioAulasMin, onibus.escolas[-1].horarioInicioAulasMax))
            self.printConj(self.miniRotas[onibus], "SUB ROTA:{} ".format(1))

    def MixedLoad(self):

        for rota in self.rotas:
            original = list(rota.percurso) # é uma lista dos locais por onde a 
            paradas=[]
            escolas=[]
            for lugar in rota.percurso:
                if isinstance(lugar,Parada):
                    paradas.append(lugar)
                if isinstance(lugar,Escola):
                    escolas.append(lugar)

            for escola in escolas:
                # Monta percurso aux
                localAnterior=None
                percurso=Rota(0)
                lotacao=0
                for local in aux:
                    if isinstance(local,Garagem):
                        percurso.percurso[local]=rota.percurso[local]
                        lotacao=0
                    elif isinstance(local,Parada):
                        inicio= self.somaSegundos(percurso.percurso[localAnterior][-1], self.tempoTrecho(self.distancia(localAnterior,local)))
                        fim= self.somaSegundos(inicio, self.tempoEmbarque(local.qtAlunos))
                        lotacao+=local.qtAlunos
                        #print( inicio,"     ", fim)
                        percurso.percurso[local]=[inicio,fim]
                    elif isinstance(local,Escola):
                        inicio= self.somaSegundos(percurso.percurso[localAnterior][-1], self.tempoTrecho(self.distancia(localAnterior,local)))
                        fim= self.somaSegundos(inicio, self.tempoDesembarque(lotacao))
                        #print( inicio,"     ", fim)
                        percurso.percurso[local]=[inicio,fim]
                        lotacao=0
                    else:
                        print("OQUEEEE????")    
                    localAnterior=local

                # Condições


         
        
         

    def UnirRotas(self):          
        ######### Método de união de mini rotas ######### 
        aux= self.conjOnibusUteis
        for onibus in self.miniRotas:
            if not onibus.anterior:
                self.rotas.append([onibus])
                aux.remove(onibus)
        
        while aux:
            print("C")
            for rota in self.rotas:
                for onibus in self.miniRotas:
                    if onibus.anterior == rota[-1]:
                        rota.append(onibus)
                        aux.remove(onibus)

                
        '''# PRINTS
        #self.printMiniRotas()
        
        i=1
        for rota in self.rotas:
            print ("************", i, "********")
            for onibus in rota:
                print(onibus)
                print(onibus.escolas)
                self.printConj(self.miniRotas[onibus],"parte de "+ str(i))
                print("     ")
            print("inicio= {}     fim= {}".format(rota[0].inicioEspediente, rota[-1].fimEspediente))
            i +=1
        '''

        # Aqui eu construo as rotas pelo model de rota
        i=0
        conjRotas=[]
        for rota in self.rotas:
            i+=1
            localAnterior=None
            percurso=Rota(i)
            for onibus in rota:
                for local in self.miniRotas[onibus]:
                    if local == self.miniRotas[onibus][0]:
                        if local in percurso.percurso:
                            percurso.percurso[local][-1]=onibus.inicioEspediente
                        else:
                            percurso.percurso[local]=[onibus.inicioEspediente,onibus.inicioEspediente]
                    elif isinstance(local,Parada):
                        inicio= self.somaSegundos(percurso.percurso[localAnterior][-1], self.tempoTrecho(self.distancia(localAnterior,local)))
                        fim= self.somaSegundos(inicio, self.tempoEmbarque(local.qtAlunos))
                        #print( inicio,"     ", fim)
                        percurso.percurso[local]=[inicio,fim]
                    elif isinstance(local,Escola):
                        inicio= self.somaSegundos(percurso.percurso[localAnterior][-1], self.tempoTrecho(self.distancia(localAnterior,local)))
                        fim= self.somaSegundos(inicio, self.tempoDesembarque(onibus.lotacao))
                        #print( inicio,"     ", fim)
                        percurso.percurso[local]=[inicio,fim]
                    else:
                        print("OQUEEEE????")    
                    localAnterior=local
            conjRotas.append(percurso)
        
        for rota in conjRotas:
            print("___________",rota.id,"___________")  
            for local in rota.percurso:
                print ("inicio: {} , fim: {} , Local: {}".format(rota.percurso[local][0],rota.percurso[local][-1],local))

       
        self.rotas=copy.copy(conjRotas) # Aqui as rotas ja estão no formato de dados do model rota
        
        #self.MixedLoad()

    def respeitaCondicoes(self, rota, onibus, parada): # Verifica todas as condições nescessárias para acrescentar uma parada na sub rota
        rotaAux= copy.copy(rota)
        rotaAux.append(parada)
        #escolas = onibus.escolas
        #escolas.append(parada.escola)
        #escolas= list(set(escolas))
        rotaAux.append(parada.escola)
        # self.printConj(rotaAux,"aaa")
        tempoRotaAux= self.tempoDaRota(rotaAux) # tempo da rota incluindo essa parada
        # BUG testar se respeita a janela de todas as escolas
        # Condições
        condLotacao= (onibus.lotacao + parada.qtAlunos)<= onibus.capacidade # Se lotação do onibus após passar na parada é menor ou igual a capacidade do onibus
        condHorarioEscola = self.somaSegundos(onibus.inicioEspediente,tempoRotaAux) <= parada.escola.horarioInicioAulasMax # Se o tempo de chegada à ultima escola será respeitado
        conTempoViagem = self.tempoRotaComCarga_(rotaAux) <= onibus.tempoMaxRota # Se o tempo de viagem com alunos no onibus respeita o limite dado
        # print(self.tempoRotaComCarga_(rotaAux),self.somaSegundos(onibus.inicioEspediente,tempoRotaAux))
        # print(condLotacao,condHorarioEscola,conTempoViagem)
        return condLotacao and condHorarioEscola and conTempoViagem

    def sbrpTestesParkSL(self,conjGaragens, conjOnibus, conjEscolas, conjParadas):# execulta os testes de tempo
        # Execulta com as instancias de Park
        # Faz análisas de tempo de execulsão

        # Insere os conjuntos de teste recebidos dos bancos de dados
        self.conjGaragens = conjGaragens # setar uma unica garagem num ponto médio entre as paradas
        self.conjOnibus = conjOnibus # setar 2000 onibus com capacidade para 66 alunos
        self.conjEscolas = sorted(conjEscolas, key= Escola.get_horarioInicioAulasMin) # setar as RSRB de Park ( http://logistics.postech.ac.kr/Mixed_SBRP_Benchmark.html )
        self.conjParadas = conjParadas #setar as RSRB de Park ( http://logistics.postech.ac.kr/Mixed_SBRP_Benchmark.html )
        
        

        contEstourou=0
        
        i=1 # Um contador pra marcar as interações 
        onibusAnterior = None
        while self.conjParadas:
            # Enquanto o conjunto de paradas não estiver vazio
            #resultado = open('resultado.txt', 'w')
            print ("************", i, "********")
            
            conjPE=[] #conjonto de paradas por escola
            for escola in self.conjEscolas:
                aux=[]
                for parada in self.conjParadas:
                    if parada.escola == escola:
                        aux.append(parada)
                if aux != []:
                    conjPE.append(aux)
            
            subRota = [] # inicializo uma subrota vazia
            parada = None

            # Cada sub rota inicializa com um novo onibus 
            onibus = random.choice(self.conjOnibus) # pega um onibus aleatório no conj de onibus
            self.conjOnibus.remove(onibus) # removo-o do conj de onibus 
            self.conjOnibusUteis.append(onibus) # acloco-o no conj de onibus utilizados
            # Ao final da contrução de sub rotas eu tento mesclar as rotas pra diminuir o numero de onibus nescessários chmando self.otimizaRotas  

            if onibusAnterior : # and há a posibilidade dele atender alguma escola if onibus anterior.fimEspediente < tempo max da escola com maior maxtime da janela
                # atribuo algumas informação de onibus anterior para o atual
                onibus.inicioEspediente = onibusAnterior.fimEspediente
                onibus.garagem= onibusAnterior.escolas[-1]
                onibus.localAtual= onibus.garagem
                onibus.anterior= onibusAnterior


            # inicializo uma sub rota com o onibus partindo do destino do anterior
            subRota.append(onibus.localAtual) # inicializo a rota partindo da garagem
            for conj in conjPE:
                lrc = self.listaRestritaDeCandidatosInicial(0.1, onibus.localAtual,conj)
                while len(subRota) == 1 : # Enquanto só tiver a garagem
                    #print(lrc) 
                    if lrc != []:
                        parada = random.choice(lrc)
                    else:
                        break
                    if self.respeitaCondicoes(subRota,onibus,parada):
                        print('PORRA')
                        subRota.append(parada)
                        onibus.escolas.append(parada.escola) # atualiza as escolas para a qual o onibus ta fazendo rota
                        onibus.escolas = list(set(onibus.escolas)) # retira repetições
                        onibus.lotacao += parada.qtAlunos # atualiza a lotação do onibus
                        onibus.localAtual = parada # atualiza local do onibus
                        self.conjParadas.remove(parada)
                    lrc.remove(parada)
                if len(subRota) >1:
                    break

            # inicializo a subrota a partir da garagem se não der
            if len(subRota) == 1:
                onibus.inicioEspediente = time(0,0,0)
                onibus.garagem= self.conjGaragens[-1]
                onibus.localAtual= onibus.garagem
                onibus.anterior=None
                subRota[0]=onibus.localAtual
                for conj in conjPE:
                    lrc = self.listaRestritaDeCandidatosInicial(0.1, onibus.localAtual,conj)
                    while len(subRota) == 1 : # Enquanto só tiver a garagem
                        #print("A") 
                        if lrc != []:
                            parada = random.choice(lrc)
                        else:
                            break
                        if self.respeitaCondicoes(subRota,onibus,parada):
                            print('MERDA')
                            subRota.append(parada)
                            onibus.escolas.append(parada.escola) # atualiza as escolas para a qual o onibus ta fazendo rota
                            onibus.escolas = list(set(onibus.escolas)) # retira repetições
                            onibus.lotacao += parada.qtAlunos # atualiza a lotação do onibus
                            onibus.localAtual = parada # atualiza local do onibus
                            self.conjParadas.remove(parada)
                        lrc.remove(parada)
                    if len(subRota) >1:
                        break
                   
            cont=0
            while(onibus.capacidade > onibus.lotacao and self.tempoRotaComCarga_(subRota + onibus.escolas) < onibus.tempoMaxRota):# Verifica condições de capacidade do onibus e tempo de rota
                cont+=1
                lrc= self.listaRestritaDeCandidatosPorEscola(0.1, onibus.localAtual)
                #print("1 LRC:{}".format(lrc))

                while lrc:
                    parada = random.choice(lrc)
                    if self.respeitaCondicoes(subRota,onibus,parada): 
                        print("+1")
                        # adiciona uma parada na sub rota e a retira do conjunto de paradas
                        #print ("condição A: add parada na subrota")
                        subRota.append(parada)
                        onibus.lotacao += parada.qtAlunos # atualiza a lotação do onibus
                        onibus.localAtual = parada # atualiza local de onibus
                        self.conjParadas.remove(parada)
                        onibus.escolas.append(parada.escola) # atualiza as escolas para a qual o onibus ta fazendo rota
                        onibus.escolas = list(set(onibus.escolas)) # retira repetições
                        cont=0
                        break
                    lrc.remove(parada)
                if cont>5:
                    cont=0
                    break
                


                '''
                if lrc != None:
                    parada = random.choice(lrc)
                    
                    #Verifica se respeita as condições nescessárias para inserção da nova parada
                    if self.respeitaCondicoes(subRota,onibus,parada): 
                        # adiciona uma parada na sub rota e a retira do conjunto de paradas
                        #print ("condição A: add parada na subrota")
                        subRota.append(parada)
                        onibus.lotacao += parada.qtAlunos # atualiza a lotação do onibus
                        onibus.localAtual = parada # atualiza local de onibus
                        self.conjParadas.remove(parada)
                        onibus.escolas.append(parada.escola) # atualiza as escolas para a qual o onibus ta fazendo rota
                        onibus.escolas = list(set(onibus.escolas)) # retira repetições

                    else:
                        #print ("condição b: add escola na subrota se não tiver tempo ou capacidade")
                        
                        #if not self.somaSegundos(onibus.fimEspediente,tempRota) < onibus.escolas[-1].horarioInicioAulasMax:
                            #print("foi tempo")
                        #if not lotacaoBeP <= onibus.capacidade:
                            #print("foi capacidade") 
                          
                        #subRota.append(onibus.escolas[-1]) # adiciona a escola como ultima parada da subRota
                        #onibus.localAtual = onibus.escolas[-1] # atualiza local de onibus
                        break
                else:
                    #print ("condição c: add escola na subrota se não tiver ais paradas na lrc")
                    #subRota.append(onibus.escolas[-1]) # adiciona a escola como ultima parada da subRota
                    #onibus.localAtual = onibus.escolas[-1] # atualiza local de onibus
                    break
                '''
            '''
            if not isinstance(subRota[-1],Escola) or subRota[-1] != onibus.escolas[-1]:
                subRota.append(onibus.escolas[-1]) # adiciona as escolas como ultimas paradas da subRota
                onibus.localAtual = onibus.escolas[-1] # atualiza local de onibus
            ''' 

            #BUG tenho que orgnizar as escolas a partir da ultima parada
            onibus.escolas = list(set(onibus.escolas))
            subRota.extend(onibus.escolas) # adiciona as escolas como ultimas paradas da subRota
            onibus.localAtual = onibus.escolas[-1] # atualiza local de onibus

            subRota = self.melhoriaDeRota(subRota) # Aplica melhoria na sub rota

            onibus.fimEspediente = self.somaSegundos(onibus.inicioEspediente, self.tempoDaRota(subRota)) # Soma ao expediente do onibuso tempo dessa sub rota
            #print("fim espediente bus {}".format(onibus.fimEspediente))
            
            
       
            # Incluia sub rota no dicionário de mini rotas
            self.miniRotas[onibus]=subRota
     
            # Prints
            #self.printConj(subRota, "SUB ROTA:{} ".format(i))
             
            if self.tempoRotaComCarga_(subRota) > 2700:
                contEstourou +=1

            #print(self.tempoDaRota(subRota))
            #print(self.tempoRotaComCarga(subRota,onibus.escolas))
            #print("Onibus utilizados= {}".format(len(self.conjOnibusUteis)))
            self.ajustaJanela_(onibus)
            onibusAnterior= onibus
            i+=1
            

        # Ajusta a janela de tempo dos onibus
        # self.ajustaJanela()

        # otimizar rotas
        self.UnirRotas() # só preciso dessa parte se as self.rotas não forem implementadas nesta função

        print(len(self.miniRotas))
        print(len(self.rotas))

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



        