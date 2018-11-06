# -*- coding: utf-8 -*-
from datetime import date, datetime, time, timedelta
from os import remove

from grasp import Grasp
from models import Escola, Garagem, Onibus, Parada

import copy

def prepararGaragemTeste(conjParadas):
    count=0
    x=0 #latitude
    y=0 #longitude
    for parada in conjParadas:
        x+= parada.latitude
        y+= parada.longitude
        count+=1
    x= x/count
    y= y/count
    return Garagem(x,y,100)

def verificarParadas(conjParadas):
    # verifica se paradas com id diferentes se são a mesma parada
    # utilizei para confirmar se nas instancia existiam paradas 
    # onde os estudantes tinham escolas diferentes de destino
    # nas instancias de park não tinham
    for p1 in conjParadas:
        for p2 in conjParadas[1:-1]:
            if p1.latitude == p2.latitude and p1.longitude == p2.longitude and p1.id != p2.id:
                print ("P1: {} e P2: {}".format(p1,p2))

def transformaParaTime(tempostr):
    tempo = time(hour=int(tempostr[:2]),minute= int(tempostr[2:]),second = 0)
    #print("hora : {} , min: {}, seg: {}".format(tempo.hour, tempo.minute, tempo.second))
    return tempo

if __name__ == '__main__':
    problema = Grasp()
    paradas = []
    escolas = []
    garagens = [] 
    frotas = []  
    # Ler os arquivos

    x=0
    y=0
    '''
    seg=3600 # quantidade de segundos a ser somado no tempo
    
    #td= datetime.strptime(str(timedelta(seconds=seg)), "%H:%M:%S").time()
    #print(td)
    #print(type(td))

    teste= time(5,25,00)

    
    deltaMais = datetime.combine(date(1,1,1), teste) + timedelta(seconds=seg)
    #deltaMenos= td +teste
    print(teste)
    print(deltaMais)
    teste= deltaMais.time()
    print(teste)
    #print(deltaMenos)
    
    rota =[0, 1,2,3]
    for idx, bus in enumerate(rota[:-1]):
        print(idx,bus)


    print(rota[-1])
    '''
    # Lendo arquivos e cria os conjuntos para teste com instanias de Park
    for i in range(1,9):
        
        #print("RSB0{}".format(i))
        # Prepara os oito conjuntos de paradas
        arqEscolas = open('SBRP_Benchmark/RSRB/RSRB0'+str(i)+'/Schools.txt', 'r')
        texto = arqEscolas.readlines()[1:] # Lê o arquivo pulando a primeira linha q é legendas
        conjEscolas = []
        for linha in texto :
            a1,a2,a3,a4,a5 = linha.split()
            a4 = transformaParaTime(a4)
            a5 = transformaParaTime(a5)
            conjEscolas.append(Escola(a1,a2,a3,a4,a5))
        escolas.append(conjEscolas)
        arqEscolas.close()

        # Prepara os oito conjuntos de paradas
        arqParadas = open('SBRP_Benchmark/RSRB/RSRB0'+str(i)+'/Stops.txt', 'r')
        texto = arqParadas.readlines()[1:] # Lê o arquivo pulando a primeira linha q é legendas
        conjParadas = []
        for linha in texto :
            a1,a2,a3,a4,a5 = linha.split()
            for escola in conjEscolas :
                if escola.id == a4:
                    a4= escola
            conjParadas.append(Parada(a1,a2,a3,a4,a5))
        paradas.append(conjParadas)
        arqParadas.close()


        # Prepara a garegem que ficará a um ponto médio entre as paradas
        garagens.append(prepararGaragemTeste(conjParadas))


        # Prepara os dois conjuntosde onibus para o teste
        conjOnibus= []
            # Prepara onibus pra teste com tempo de atendimento 2700
        aux= []
        for j in range(3000):
            aux.append(Onibus(j,garagens[-1],2700,66))
        conjOnibus.append(aux)
            # Prepara onibus pra teste com tempo de atendimento 5400
        aux= []
        for k in range(3000):
            aux.append(Onibus(k,garagens[-1],5400,66))
        conjOnibus.append(aux)

        frotas.append(conjOnibus)
    
   
       
    '''
    # mostrar os conjuntos
    for i in range(1):
        
        for parada in paradas[i]:
            print (parada)
        
        print(garagens[i])

        for escola in escolas[i]:
            print(escola)
    #    
        for conjOnibus in frotas[i]:
            for onibus in conjOnibus:
                print(onibus)
    '''
    
    #print(frotas[7][0])
    # frotas[instancias][restrição de tempo]
    # Chama o teste
    '''
    aux=[1,2,3,4,5,6,7,8,9]
    x=[7,8,9]
    for i in aux[1:-(len(x))]:
        print(i)

    for i in  range(2, len(aux)-(len(x))):
        print(i ,  aux[i], aux[i-1])

    
    '''
    problema.sbrpTestesParkSL([garagens[7]],frotas[7][0], escolas[7],paradas[7])
    '''
    for onibus in problema.conjOnibusUteis:
        print(onibus.escolas)
    '''
    