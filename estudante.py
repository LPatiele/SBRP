# -*- coding: utf-8 -*-
import random
from escola import Escola


class Estudante:
    def __init__(self, *args, **kwargs):
        self.nome =  ''.join(random.choice("asdfghjklçqwertyuiopzxcvbnm") for _ in range(5) ) 
        self.escola = Escola()
        self.endereço = ''
        self.latitude = random.randint(1,10)
        self.longitude = random.randint(1,10)       


# if __name__ == '__main__' :
#     pa = Estudante()
#     pb = Estudante()
#     pa.nome = 'teste1'
#     pb.nome = 'teste2'
#     pa.kuyu()
#     pb.kuyu()