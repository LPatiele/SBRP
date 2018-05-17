# -*- coding: utf-8 -*-
import random
from datetime import time

class Escola:
    def __init__(self, *args, **kwargs):
        self.nome= ''.join(random.choice("asdfghjklçqwertyuiopzxcvbnm") for _ in range(10) ) 
        self.endereço= ''
        # self.latitude= random.randint(1,10)
        # self.longitude= random.randint(1,10)
        self.horarioInicioAulasMin = 1
        self.horarioInicioAulasMax = 800.0 #ta como se fosse minutos
        self.matrizDistancia = {}

    def __str__(self):
        return  'Escola Nome: ' + str(self.nome)  #+' Latitude: ' + str(self.latitude) + ' Longitude: ' + str(self.longitude) 

class Estudante:
    def __init__(self, *args, **kwargs):
        self.nome =  ''.join(random.choice("asdfghjklçqwertyuiopzxcvbnm") for _ in range(5) ) 
        self.escola = Escola()
        self.endereço = ''
        self.latitude = random.randint(1,10)
        self.longitude = random.randint(1,10)       

class Garagem:
    def __init__(self, *args, **kwargs):
        self.nome= ''.join(random.choice("asdfghjklçqwertyuiopzxcvbnm") for _ in range(3) ) 
        self.endereço= ''
        # self.latitude= round(random.uniform(-1000.0,1000.0), 5) 
        # self.longitude= round(random.uniform(-1000.0,1000.0), 5) 
        self.matrizDistancia = {}
        #self.capacidade= random.randint(1,5)

    def __str__(self):
        return  'Garagem Nome: ' + str(self.nome) #+' Latitude: ' + str(self.latitude) + ' Longitude: ' + str(self.longitude) 

        #self.onibus= []
        ## gerar onibus
        # for i in range(self.capacidade):
        #     novoOnibus= Onibus(self)
        #     onibus.append(novoOnibus)

class Onibus:
    def __init__(self, garagem):
        self.identificação= random.randint(1000,3000)
        self.garagem= garagem
        self.horarioAtendimento= 333.0
        self.capacidade= 10
        self.lotacao=0
        self.escola= object
        self.localAtual= garagem
        self.tempoRota= 0.0

    def __str__(self):
        # try:
        #     return 'Identificação: ' + str(self.identificação) + ' Garagem: ' + str(self.garagem.nome) + ' Escola: ' + str(self.escola.nome)
        # except :
        return 'Identificação: ' + str(self.identificação) + ' Garagem: ' + str(self.garagem.nome)


class Parada:
    def __init__(self, escola, id):
        self.identificador = id
        # self.latitude =  round(random.uniform(-1000.0,1000.0), 5) 
        # self.longitude = round(random.uniform(-1000.0,1000.0), 5) 
        self.qtAlunos = 1 # random.randint(1,3)
        self.alunos = []
        self.escola = escola
        self.matrizDistancia = {}
        
    def __str__(self):
        return ' Parada ID: '+ str(self.identificador)  #+ ' Latitude: ' + str(self.latitude) + ' Longitude: ' + str(self.longitude) + ' Escola: ' + str(self.escola.nome)
        