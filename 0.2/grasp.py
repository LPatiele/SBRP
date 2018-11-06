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
        self.rotas=[] # para cada rota é designado um onibus distinto
        self.miniRotas={} # dicionário chave=onibus e valor=rota do onibus

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

    def tempoRotaComCarga(self,rota,escolas): #conta o tempo da rota em que há alunos no onibus
        aux = copy.copy(rota)
        aux.extend(escolas)
        # retorna o tempo da rota desconsiderando a viagem vazia da garagem à primeira parada
        return self.tempoDaRota(aux) - self.tempoTrecho(self.distancia(aux[0],aux[1]))

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

    def printMiniRotas(self):
        for onibus in self.conjOnibusUteis:
            print("______________________________________________________________________________")
            print ("onibus: lot {}, Ti {}, Tf {}, escl {}".format(onibus.lotacao,onibus.inicioEspediente, onibus.fimEspediente, onibus.escolas[-1].id ))
            print("escola: inicio {} , fim {}".format(onibus.escolas[-1].horarioInicioAulasMin, onibus.escolas[-1].horarioInicioAulasMax))
            self.printConj(self.miniRotas[onibus], "SUB ROTA:{} ".format(1))

    def otimizaRotas(self): 
        ######### Método 3 de união de mini rotas #########
        for onibus in self.miniRotas:
            
            if self.rotas == []:
                self.rotas.append([onibus])
                
            else:
                novaRota= True # marca se esse onibus foi inserido ou se será o inicio de uma nova rota
                for rota in self.rotas:
                       
                    if onibus.fimEspediente < rota[0].inicioEspediente or self.somaSegundos( rota[0].fimEspediente , self.diferencaTempo(rota[0].inicioEspediente, onibus.fimEspediente)) <= rota[0].escolas[-1].horarioInicioAulasMax:
                        # tento colocar no inicio da rota
                        if not onibus.fimEspediente < rota[0].inicioEspediente: #  ajusto a janela do bus caso nescessário
                            rota[0].fimEspediente = self.somaSegundos( rota[0].fimEspediente, self.diferencaTempo(rota[0].inicioEspediente, onibus.fimEspediente))
                            rota[0].inicioEspediente = self.somaSegundos(rota[0].inicioEspediente, self.diferencaTempo(rota[0].inicioEspediente, onibus.fimEspediente))
                        rota.insert(0,onibus)
                        novaRota= False
                    elif rota[-1].fimEspediente < onibus.inicioEspediente or self.somaSegundos(onibus.fimEspediente, self.diferencaTempo(onibus.inicioEspediente, rota[-1].fimEspediente)) <= onibus.escolas[-1].horarioInicioAulasMax:
                        # tento colocar no final da rota
                        if not rota[-1].fimEspediente < onibus.inicioEspediente: #  ajusto a janela do bus caso nescessário
                            onibus.fimEspediente = self.somaSegundos(onibus.fimEspediente, self.diferencaTempo(onibus.inicioEspediente, rota[-1].fimEspediente))
                            onibus.inicioEspediente =self.somaSegundos( onibus.inicioEspediente, self.diferencaTempo(onibus.inicioEspediente, rota[-1].fimEspediente))
                        rota.append(onibus)
                        novaRota= False
                    elif len(rota)>1:
                        # tento colocar no meio da rota
                        for idx, bus in enumerate(rota[:-1]): # comparar entre bus e rota[idx+1]
                            # se o tempo da rota + os novos trechos for menor ou igual 
                            # ao espaço de tempo entre a mini rota do bus atual e do proximo
                            # e o ajuste de onibus.fimEspediente estiver dentro da janela de tempo da escolas eu insiro aqui
                            if (self.tempoRotaComCarga_(self.miniRotas[onibus]) + self.tempoTrecho(self.distancia(self.miniRotas[bus][-1], self.miniRotas[onibus][1]))) <= self.diferencaTempo(bus.fimEspediente,rota[idx+1].inicioEspediente):
                                # Verifico se o tempo de percurso com alunos + o tempo do fim da linha de bus ate a primeira parada de onibus é menos que o tempo entre o fim da mini rota de bus e o inicio da minirota do próximo onibus
                                condA = self.somaSegundos(bus.fimEspediente , self.tempoRotaComCarga_(self.miniRotas[onibus]) + self.tempoTrecho(self.distancia(self.miniRotas[bus][-1], self.miniRotas[onibus][1]))) <= onibus.escolas[-1].horarioInicioAulasMax
                                # condA é um verificador se respeita a restrição de tempo máximo da escolas do onibus se ajustar o tempo a partir do fim da mini rota anterior
                                condB = self.somaSegundos(bus.fimEspediente , self.tempoRotaComCarga_(self.miniRotas[onibus]) + self.tempoTrecho(self.distancia(self.miniRotas[bus][-1], self.miniRotas[onibus][1]))) >= onibus.escolas[-1].horarioInicioAulasMin
                                # condA é um verificador se respeita a restrição de tempo minimo da escolas do onibus se ajustar o tempo a partir do fim da mini rota anterior
                                try:
                                    condC = self.subSegundos(rota[idx+1].inicioEspediente ,(self.tempoTrecho(self.distancia(self.miniRotas[onibus][-1], self.miniRotas[rota[idx+1]][1])))) <= onibus.escolas[-1].horarioInicioAulasMax
                                    # condC é um verificador se respeita a restrição de tempo máximo da escolas do onibus se ajustar o tempo tendo como tempo final o tempo da inicio da próxima rota
                                except:
                                    condC = False
                                try:
                                    condD = self.subSegundos(rota[idx+1].inicioEspediente ,(self.tempoTrecho(self.distancia(self.miniRotas[onibus][-1], self.miniRotas[rota[idx+1]][1])))) >= onibus.escolas[-1].horarioInicioAulasMin
                                    # condD é um verificador se respeita a restrição de tempo minimo da escolas do onibus se ajustar o tempo tendo como tempo final o tempo da inicio da próxima rota
                                except:
                                    condD = False
                                if (condA and condB):
                                    # munda a garagem de onibus e de rota[idx+1]
                                    onibus.garagem =self.miniRotas[bus][-1]
                                    self.miniRotas[onibus][0]=onibus.garagem
                                    rota[idx+1].garagem =self.miniRotas[onibus][-1]
                                    self.miniRotas[rota[idx+1]][0]=rota[idx+1].garagem
                                    # Altero o tempo de inicio e fim da rota de onibus
                                    onibus.inicioEspediente = bus.fimEspediente
                                    onibus.fimEspediente = self.somaSegundos(onibus.inicioEspediente , self.tempoDaRota(self.miniRotas[onibus]))
                                    #Insere onibus na rota
                                    rota.insert(idx+1,onibus)
                                    novaRota= False
                                elif (condC and condD): 
                                    # munda a garagem de onibus e de rota[idx+1]
                                    onibus.garagem =self.miniRotas[bus][-1]
                                    self.miniRotas[onibus][0]=onibus.garagem
                                    rota[idx+1].garagem =self.miniRotas[onibus][-1]
                                    self.miniRotas[rota[idx+1]][0]=rota[idx+1].garagem
                                    # Altero o tempo de inicio e fim da rota de onibus
                                    onibus.fimEspediente = rota[idx+1].inicioEspediente
                                    onibus.inicioEspediente = self.subSegundos(onibus.fimEspediente,self.tempoDaRota(self.miniRotas[onibus]))
                                    # Insere onibus na rota
                                    rota.insert(idx+1,onibus)
                                    novaRota= False
                                else:
                                    pass
                            if not novaRota:
                                break            
                    
                if novaRota:
                    self.rotas.append([onibus])

        '''
        ######### Método 3 de união de mini rotas #########
        aux = copy.copy(self.conjOnibusUteis)
        while aux:
            bus= random.choice(aux)
            if self.rotas == []:
                self.rotas.append([bus])
            else: # tenta inserir nas rotas que ja existem
                pass


        ######### Método 1 de união de mini rotas #########
        aux = copy.copy(self.conjOnibusUteis)
        
        for onibus1 in aux:
            rota = []
            aux.remove(onibus1)
            marcador= None
            for onibus2 in aux: # Verifico se da pra colocar algum percurso antes
                if onibus2.fimEspediente < onibus1.inicioEspediente:
                    rotaAux= copy.copy(self.miniRotas[onibus1])
                    rotaAux[0]= self.miniRotas[onibus2][-1]
                    tempo= self.subSegundos(onibus1.fimEspediente,self.tempoDaRota(rotaAux))
                    if onibus2.fimEspediente < tempo:
                        marcador= onibus2
                        self.miniRotas[onibus1]= rotaAux
                        onibus1.inicioEspediente= tempo
                        break
            if marcador:
                #rota.append(self.miniRotas[marcador])
                rota.append(marcador)
                aux.remove(marcador)

            #rota.append(self.miniRotas[onibus1])
            rota.append(onibus1)
            
            marcador= None
            for onibus2 in aux: # Verifico se da pra colocar algum percurso depois
                if onibus1.fimEspediente < onibus2.inicioEspediente:
                    rotaAux= copy.copy(self.miniRotas[onibus2])
                    rotaAux[0]= self.miniRotas[onibus1][-1]
                    tempo= self.subSegundos(onibus2.fimEspediente,self.tempoDaRota(rotaAux))
                    if onibus1.fimEspediente < tempo:
                        marcador= onibus2
                        self.miniRotas[onibus2]= rotaAux
                        onibus2.inicioEspediente= tempo
                        break
            if marcador:
                #rota.append(self.miniRotas[marcador])
                rota.append(marcador)
                aux.remove(marcador)
            

            self.rotas.append(rota)
        '''

        '''
        cont1=0
        cont2=0
        for id,rota1 in enumerate(self.rotas): # a rotaX é a rota que estou tentando eliminar na interação
            for onibus1 in rota1:
                removido= False
                for rota2 in self.rotas: # aqui eu percorro as outras rotas tentanto inserir a miniRota do onibus
                    for idx, onibus2 in enumerate(rota2[:-1]):
                        print("o")
                        cont1 +=1
                        if (self.tempoRotaComCarga_(self.miniRotas[onibus1]) + self.tempoTrecho(self.distancia(self.miniRotas[onibus2][-1], self.miniRotas[onibus1][0]))) <= self.diferencaTempo(rota[idx].fimEspediente,onibus2.inicioEspediente):
                            # se o tempo do percurso realizado pelo onibus
                            cont2 +=1
                            rota2.insert(idx+1,onibus1)
                            rota1.remove(onibus1)
                            removido=True
                            break
                            print ("l")
                    if removido:
                        break
                if removido:
                    break

        for rota in self.rotas:
            if len(rota) == 0:
                self.rotas.remove(rota)
                print("porra")
        
        '''
        #self.printMiniRotas()
        i=1
        for rota in self.rotas:
            print ("************", i, "********")
            for onibus in rota:
                print(onibus)
                self.printConj(self.miniRotas[onibus],"parte de "+ str(i))
                print("     ")
            print("inicio= {}     fim= {}".format(rota[0].inicioEspediente, rota[-1].fimEspediente))
            i +=1

       

        

                

    def unirMiniRotas(self,onibus1,onibus2):
        auxBus1= copy.copy(onibus1)
        auxBus2= copy.copy(onibus2)
        rota1= copy.copy(self.miniRotas[onibus1])
        rota2= copy.copy(self.miniRotas[onibus2])
        rota2[0]= rota1[-1] 
        if auxBus1.fimEspediente < auxBus2.inicioEspediente:
            pass
    
    def respeitaCondicoes(self, rota, onibus, parada): # Verifica todas as condições nescessárias para acrescentar uma parada na sub rota
        rotaAux= copy.copy(rota)
        rotaAux.append(parada)
        tempoRotaAux= self.tempoDaRota(rotaAux) # tempo da rota incluindo essa parada
        conTempoViagem = self.tempoRotaComCarga(rotaAux,[parada.escola]) # tempo de viagem com alunos no onibus
        # Condições
        condLotacao= (onibus.lotacao + parada.qtAlunos)<= onibus.capacidade # Se lotação do onibus após passar na parada é menor ou igual a capacidade do onibus
        condHorarioEscola = self.somaSegundos(onibus.inicioEspediente,tempoRotaAux) <= parada.escola.horarioInicioAulasMax # Se o tempo de chegada à escola será respeitado
        conTempoViagem = self.tempoRotaComCarga(rotaAux,[parada.escola]) <= onibus.tempoMaxRota # Se o tempo de viagem com alunos no onibus respeita o limite dado
        return condLotacao and condHorarioEscola and conTempoViagem

    def sbrpTestesParkSL(self,conjGaragens, conjOnibus, conjEscolas, conjParadas):# execulta os testes de tempo
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
            #print ("************", i, "********")
            
            subRota = [] # inicializo uma subrota vazia
            parada = None

            # Cada sub rota inicializa com um novo onibus 
            onibus = random.choice(self.conjOnibus) # pega um onibus aleatório no conj de onibus
            self.conjOnibus.remove(onibus) # removo-o do conj de onibus 
            self.conjOnibusUteis.append(onibus) # acloco-o no conj de onibus utilizados
            subRota.append(onibus.localAtual) # inicializo a rota partindo da garagem
            # Ao final da contrução de sub rotas eu tento mesclar as rotas pra diminuir o numero de onibus nescessários

            # BUG: Da pra trocar os dois while por do/while com carga mista ????

            # inicializo uma sub rota
            while len(subRota) == 1: # Enquanto só tiver a garagem
                lrc = self.listaRestritaDeCandidatosInicial(0.1, onibus.localAtual)
                parada = random.choice(lrc)
                if self.respeitaCondicoes(subRota,onibus,parada):
                    subRota.append(parada)
                    onibus.escolas.append(parada.escola) # atualiza as escolas para a qual o onibus ta fazendo rota
                    onibus.escolas = list(set(onibus.escolas)) # retira repetições
                    onibus.lotacao += parada.qtAlunos # atualiza a lotação do onibus
                    onibus.localAtual = parada # atualiza local do onibus
                    self.conjParadas.remove(parada)

            while(onibus.capacidade > onibus.lotacao and self.tempoRotaComCarga(subRota,onibus.escolas) < onibus.tempoMaxRota):# Verifica condições de capacidade do onibus e tempo de rota

                lrc= self.listaRestritaDeCandidatosPorEscola(0.1, onibus.localAtual)
                #print("1 LRC:{}".format(lrc))
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

                    else:
                        #print ("condição b: add escola na subrota se não tiver tempo ou capacidade")
                        '''
                        if not self.somaSegundos(onibus.fimEspediente,tempRota) < onibus.escolas[-1].horarioInicioAulasMax:
                            print("foi tempo")
                        if not lotacaoBeP <= onibus.capacidade:
                            print("foi capacidade") 
                        '''   
                        subRota.append(onibus.escolas[-1]) # adiciona a escola como ultima parada da subRota
                        onibus.localAtual = onibus.escolas[-1] # atualiza local de onibus
                        break
                else:
                    #print ("condição c: add escola na subrota se não tiver ais paradas na lrc")
                    subRota.append(onibus.escolas[-1]) # adiciona a escola como ultima parada da subRota
                    onibus.localAtual = onibus.escolas[-1] # atualiza local de onibus
                    break
            
            if not isinstance(subRota[-1],Escola):
                subRota.append(onibus.escolas[-1]) # adiciona as escolas como ultimas paradas da subRota
                onibus.localAtual = onibus.escolas[-1] # atualiza local de onibus
             
            
            
            subRota = self.melhoriaDeRota(subRota) # Aplica melhoria na sub rota

            onibus.fimEspediente = self.somaSegundos(onibus.inicioEspediente, self.tempoDaRota(subRota)) # Soma ao expediente do onibuso tempo dessa sub rota
            #print("fim espediente bus {}".format(onibus.fimEspediente))
            # Atualiza a permissão de atender mais rotas do onibus
            
       
            # Incluia sub rota no conj de rotas e no dicionário de soluções
            #self.rotas.append(subRota)
            self.miniRotas[onibus]=subRota
     
            # Prints
            #self.printConj(subRota, "SUB ROTA:{} ".format(i))
             
            if self.tempoRotaComCarga(subRota,onibus.escolas) > 2700:
                contEstourou +=1

            #print(self.tempoDaRota(subRota))
            #print(self.tempoRotaComCarga(subRota,onibus.escolas))
            #print("Onibus utilizados= {}".format(len(self.conjOnibusUteis)))
            
            i+=1
            

        # Ajusta a janela de tempo dos onibus
        self.ajustaJanela()

        # otimizar rotas
        self.otimizaRotas()

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



        