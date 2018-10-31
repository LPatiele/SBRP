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
        self.horarioInicioAulasMin = hmin   # BUG mudar grasp pra aceitar time
        self.horarioInicioAulasMax = hmax   # BUG mudar grasp pra aceitar time
        #self.matrizDistancia = {}

    def get_horarioInicioAulasMin(self):
        return self.horarioInicioAulasMin

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
    def __init__(self,id, garagem, tempoMaxRota, capacidade):
        self.id = id
        self.garagem = garagem
        self.permissaoAtendimento = True
        self.capacidade = capacidade # 66 para os testes
        self.inicioEspediente = time(3,0,0)
        self.fimEspediente = time(0,0,0) # BUG mudar grasp pra aceitar time
        self.lotacao = 0 
        self.escolas = []
        self.localAtual = garagem
        self.tempoMaxRota = tempoMaxRota # 2700 (45 min) e 5400 (90 min) para os testes tempo maximo de um aluno na rota

    def __str__(self):
        # try:
        #     return 'Identificacao: ' + str(self.identificacao) + ' Garagem: ' + str(self.garagem.nome) + ' Escola: ' + str(self.escolas.nome)
        # except :
        return 'ONIBUS Id:{} inicio:{} fim:{} capacidade:{} permissaoAtendimento:{}'.format(self.id, self.inicioEspediente, self.fimEspediente, self.capacidade,self.permissaoAtendimento)

class Parada:
    def __init__(self, id, x, y, escolas, quantAlunos):
        self.id = id
        self.latitude =  float(x)
        self.longitude = float(y)
        self.qtAlunos = int(quantAlunos) # random.dranint(1,3)
        self.escola = escolas
        #self.matrizDistancia = {}
        
    def __str__(self):
        return ' PARADA ID: '+ str(self.id)  + ' Latitude: ' + str(self.latitude) + ' Longitude: ' + str(self.longitude) + ' Escola: ' + str(self.escola.id)
        


