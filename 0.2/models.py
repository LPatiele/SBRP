# -*- coding: utf-8 -*-
import random
from datetime import time

class Escola:
    def __init__(self, id, x, y, hmin,hmax):
        self.nome= ''.join(random.choice("asdfghjklçqwertyuiopzxcvbnm") for _ in range(10) ) 
        self.endereco= ''
        self.id= id
        self.latitude= float(x)
        self.longitude= float(y)
        self.horarioInicioAulasMin = float(hmin)
        self.horarioInicioAulasMax = float(hmax)
        #self.matrizDistancia = {}

    def __str__(self):
        return  'ESCOLA id:{}, latitude:{}, longitude:{}, hmin:{}, hmax:{}'.format(self.id,self.latitude,self.longitude,self.horarioInicioAulasMin,self.horarioInicioAulasMax)

class Estudante:
    def __init__(self, *args, **kwargs):
        self.nome =  ''.join(random.choice("asdfghjklçqwertyuiopzxcvbnm") for _ in range(5) ) 
        self.escola = Escola()
        self.endereco = ''
        self.latitude = random.randint(1,10)
        self.longitude = random.randint(1,10)  

        def __str__(self):
            return  'Estudante Nome: ' + str(self.nome)

class Garagem:
    def __init__(self,x,y,qtOnibus):
        self.nome= ''.join(random.choice("asdfghjklçqwertyuiopzxcvbnm") for _ in range(3) ) 
        self.endereco= ''
        self.latitude= round(float(x),1) 
        self.longitude= round(float(y),1)
        #self.matrizDistancia = {}
        #self.capacidade= random.randint(1,5)
        self.lotacao= qtOnibus

    def __str__(self):
        return  'GARAGEM x:{}  y:{}'.format(self.latitude, self.longitude)


class Onibus:
    def __init__(self, garagem, horarioAtendimento, capacidade):
        self.id= random.randint(1000,3000)
        self.garagem= garagem
        self.horarioAtendimento= horarioAtendimento # 2700 e 5400 para os testes
        self.capacidade= capacidade # 66 para os testes
        self.lotacao=0
        self.escola= []
        self.localAtual= garagem
        self.tempoRota= 0.0

    def __str__(self):
        # try:
        #     return 'Identificacao: ' + str(self.identificacao) + ' Garagem: ' + str(self.garagem.nome) + ' Escola: ' + str(self.escola.nome)
        # except :
        return 'ONIBUS Id:{} garagem:{},{} capacidade:{} tempo:{}'.format(self.id, self.garagem.latitude, self.garagem.longitude, self.capacidade,self.horarioAtendimento)


class Parada:
    def __init__(self, id, x, y, escolas, quantAlunos):
        self.id = id
        self.latitude =  float(x)
        self.longitude = float(y)
        self.qtAlunos = int(quantAlunos) # random.randint(1,3)
        self.escola = escolas
        #self.matrizDistancia = {}
        
    def __str__(self):
        return ' PARADA ID: '+ str(self.id)  + ' Latitude: ' + str(self.latitude) + ' Longitude: ' + str(self.longitude) #+ ' Escola: ' + str(self.escola.nome)
        


