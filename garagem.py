# -*- coding: utf-8 -*-
import random
from datetime import time
#from onibus import Onibus


class Garagem:
    def __init__(self, *args, **kwargs):
        self.nome= ''.join(random.choice("asdfghjklçqwertyuiopzxcvbnm") for _ in range(3) ) 
        self.endereço= ''
        self.latitude= round(random.uniform(-1000.0,1000.0), 5) 
        self.longitude= round(random.uniform(-1000.0,1000.0), 5) 
        #self.capacidade= random.randint(1,5)

    def __str__(self):
        return  'Nome: ' + str(self.nome)+' Latitude: ' + str(self.latitude) + ' Longitude: ' + str(self.longitude) 

        #self.onibus= []
        ## gerar onibus
        # for i in range(self.capacidade):
        #     novoOnibus= Onibus(self)
        #     onibus.append(novoOnibus)

       




    