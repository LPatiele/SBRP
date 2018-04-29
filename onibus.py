# -*- coding: utf-8 -*-
import random
from datetime import time
from garagem import Garagem
from escola import Escola


class Onibus:
    def __init__(self, garagem):
        self.identificação= random.randint(1000,3000)
        self.garagem= garagem
        self.horarioAtendimento= 60.0
        self.capacidade= 5
        self.lotacao=0
        self.escola= object
        self.localAtual= garagem
        self.tempoRota= 0.0

    def __str__(self):
        # try:
        #     return 'Identificação: ' + str(self.identificação) + ' Garagem: ' + str(self.garagem.nome) + ' Escola: ' + str(self.escola.nome)
        # except :
        return 'Identificação: ' + str(self.identificação) + ' Garagem: ' + str(self.garagem.nome)
        

    
    
