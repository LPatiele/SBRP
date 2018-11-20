# -*- coding: utf-8 -*-
import random
from datetime import time


class Escola:
    def __init__(self, id, x, y, hmin,hmax):
        self.id= id
        self.latitude= float(x)
        self.longitude= float(y)
        self.horarioInicioAulasMin = hmin #  time(0,0,0)  # BUG mudar grasp pra aceitar time
        self.horarioInicioAulasMax = hmax #  time(8,0,0)  # BUG mudar grasp pra aceitar time
        self.janelaInicioMin= None
        self.janelaInicioMax= None

    def get_horarioInicioAulasMin(self):
        return self.horarioInicioAulasMin

    def get_horarioInicioAulasMax(self):
        return self.horarioInicioAulasMax

    def __str__(self):
        return  'ESCOLA id:{}, latitude:{}, longitude:{}, hmin:{}, hmax:{}'.format(self.id,self.latitude,self.longitude,self.horarioInicioAulasMin,self.horarioInicioAulasMax)



class Garagem:
    def __init__(self,x,y,qtOnibus):
        
        self.latitude= round(float(x),1) 
        self.longitude= round(float(y),1)
        

    def __str__(self):
        return  'GARAGEM x:{}  y:{}'.format(self.latitude, self.longitude)

class Onibus:
    def __init__(self,id, garagem, tempoMaxRota, capacidade):
        self.id = id
        self.garagem = garagem
        self.capacidade = capacidade # 66 para os testes
        self.inicioEspediente = time(0,0,0)
        self.fimEspediente = time(0,0,0) # BUG mudar grasp pra aceitar time
        self.lotacao = 0 
        self.escolas = []
        self.localAtual = garagem
        self.tempoMaxRota = tempoMaxRota # 2700 (45 min) e 5400 (90 min) para os testes tempo maximo de um aluno na rota
        self.anterior=None

    def __str__(self):
        return 'ONIBUS Id:{} inicio:{} fim:{} lotação:{}'.format(self.id, self.inicioEspediente, self.fimEspediente, self.lotacao)

class Parada:
    def __init__(self, id, x, y, escola, quantAlunos):
        self.id = id
        self.latitude =  float(x)
        self.longitude = float(y)
        self.qtAlunos = int(quantAlunos) # random.dranint(1,3)
        self.escola = escola
        
    def __str__(self):
        return ' PARADA ID: '+ str(self.id)  + ' Latitude: ' + str(self.latitude) + ' Longitude: ' + str(self.longitude) + ' Escola: ' + str(self.escola.id)+ ' QT. Alunos'+ str(self.qtAlunos)
        

class Rota:
    def __init__(self,id):
        self.id = id
        self.percurso= {} #dicionario de local(chave) e horário que chega e sai deste local(valor, lista de duas hora)
        
