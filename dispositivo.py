# Codigo: Dispositivo MQTT
# Autor: Gustavo Lidani

import paho.mqtt.client as mqtt
import time

import random
from hal import temperature, humidity, heater
from definitions import username, password, client_ids, server, port

def bin2str(text, encoding = 'utf-8'):
    """Converts a binary to Unicode string by removing all non Unicode char
    text: binary string to work on
    encoding: output encoding *utf-8"""
    return text.decode(encoding, 'ignore')

def message(client, _, msg):
    vector = (msg.payload.decode()).split(',')
    heater_status = heater('on' if vector[1] == '1' else 'off')

    client_id = bin2str(client._client_id)

    publish(client, 'response', f'ok,{vector[0]}')

    print(f'{client_id}: {heater_status}')

    # Atualiza o estado do cliente
    states[client_id]['heater'] = 'on' if vector[1] == '1' else 'off'

    print(vector)

def publish(client, channel, value):
    # print(f'publicando {value} no canal {channel}')

    client.publish(f'v1/{username}/things/{bin2str(client._client_id)}/data/{channel}', value)

def init(client_id, callback):
    # conexao inicial
    client = mqtt.Client(client_id)
    client.username_pw_set(username, password)
    client.connect(server, port) # https://cayenne.mydevices.com
    client.on_message = callback # Callback function
    client.subscribe(f'v1/{username}/things/{client_id}/cmd/3', 2)

    return client

# Inicializa
clients, states = [], {}

for client_id in client_ids:
    print(f'Inicializando cliente {client_id}...')

    client = init(client_id, message)
    client.loop_start()

    clients.append(client)

    states[client_id] = {
        # Randomiza a temperatura inicial
        'temp': random.randrange(10, 40),
        'humidity': 0,
        'heater': 'on'
    }
    
print(f'\n{len(clients)} clientes inicializados com sucesso...\n')

# Loop
while True:

    for client in clients:
        client_id = bin2str(client._client_id)
        state = states[client_id]

        states[client_id]['temp'] = temp = temperature(state['temp'], 5 if state['heater'] == 'on' else -5)

        if temp >= 32:
            states[client_id]['heater'] = 'off'
            # Atualiza o status do botão
            publish(client, '5', '0')

        elif temp <= 28:
            states[client_id]['heater'] = 'on'
            # Atualiza o status do botão
            publish(client, '5', '1')

        else: publish(client, '5', '0' if states[client_id]['heater'] == 'off' else '1')

        publish(client, '0', temp)
        publish(client, '1', humidity())

        print(f'{client_id} sincronizado')

    time.sleep(5)
