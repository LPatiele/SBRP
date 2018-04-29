# -*- coding: utf-8 -*-
import random
from escola import Escola


class Parada:
    def __init__(self, escola):
        self.latitude =  round(random.uniform(-1000.0,1000.0), 5) 
        self.longitude = round(random.uniform(-1000.0,1000.0), 5) 
        self.qtAlunos = random.randint(1,3)
        self.alunos = []
        self.escola = escola
        
    def __str__(self):
        return 'Latitude: ' + str(self.latitude) + ' Longitude: ' + str(self.longitude) + ' Escola: ' + str(self.escola.nome)
        
        