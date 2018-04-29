# -*- coding: utf-8 -*-
import random
from datetime import time

class Escola:
    def __init__(self, *args, **kwargs):
        self.nome= ''.join(random.choice("asdfghjklçqwertyuiopzxcvbnm") for _ in range(10) ) 
        self.endereço= ''
        self.latitude= random.randint(1,10)
        self.longitude= random.randint(1,10)
        self.horarioInicioAulasMin = 1
        self.horarioInicioAulasMax = 60 #ta como se fosse minutos

    def __str__(self):
        return  'Nome: ' + str(self.nome)+' Latitude: ' + str(self.latitude) + ' Longitude: ' + str(self.longitude) 

# if __name__ == '__main__' :
#     pa = Escola()
#     pa.horarioInicioAulas= time(10,20)#pra setar a hora
#     pb = Escola()
#     pb.horarioInicioAulas= time()
    
#     pb.horarioInicioAulas=pb.horarioInicioAulas.replace(hour=11,minute=22)# pra alterar a hora

#     print(pa.horarioInicioAulas)
#     print(pb.horarioInicioAulas)

        
            