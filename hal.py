# Codigo: HAL (hardware abstraction layer)
# Autor: Gustavo Lidani

import random

def temperature(temp, factor):
    return temp + factor

def humidity():
    return random.randrange(10, 96)

def heater(state: str):
    if state == 'on':
        return 'Aquecedor LIGADO'
    else:
        return 'Aquecedor DESLIGADO'
