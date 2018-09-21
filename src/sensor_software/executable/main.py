#!/usr/bin/env python3

import sys
import os
import signal
from Adafruit_SHT31 import *
from dotenv import load_dotenv
import websocket
import time
import logging
import threading
import json
import gpiozero

env_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

output_devices = {}


# Non-blocking interval class

class Interval:
    def __init__(self, interval, action):
        self.interval = interval
        self.action = action
        self.stopEvent = threading.Event()
        thread = threading.Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self):
        next_time = time.time() + self.interval
        while not self.stopEvent.wait(next_time - time.time()):
            next_time += self.interval
            self.action()

    def cancel(self):
        self.stopEvent.set()


# Handle exit codes

def signal_handler(sig, frame):
    logging.info('Exiting...')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


# Full app. Sorry this is all in one file for now


def send(ws, message_id, data=None):
    message = {
        "id": message_id,
    }
    if data:
        message['data'] = data
    ws.send(json.dumps(message))


def on_message(ws, text_message):
    try:
        message = json.loads(text_message)
    except Exception as err:
        logging.error('Unable to parse message {}: {}'.format(text_message, err))
        return
    if message['id'] == 'pong':
        return
    logging.info('Received message: {}'.format(message))
    logging.info(message)
    if message['id'] in ['setup_relay', 'turn_on_relay', 'turn_off_relay']:
        if not message['data']:
            return send(ws, 'error', {
                "message": "Missing message data."
            })
        elif not message['data']['pin'] or type(message['data']['pin']) != int:
            return send(ws, 'error', {
                "message": "Missing parameter `pin` (integer) in message data"
            })
        try:
            desired_pin = message['data']['pin']
            if desired_pin not in output_devices or not output_devices[desired_pin] or message['id'] == 'setup_relay':
                output_devices[desired_pin] = gpiozero.OutputDevice(desired_pin, active_high=False,
                                                                    initial_value=False)
            if message['id'] == 'setup_relay':
                logging.info('Successfully set up {} as relay'.format(desired_pin))
            elif message['id'] == 'turn_on_relay':
                output_devices[desired_pin].on()
                logging.info('Successfully turned on pin {}'.format(desired_pin))
            elif message['id'] == 'turn_off_relay':
                output_devices[desired_pin].off()
                logging.info('Successfully turned off pin {}'.format(desired_pin))
        except Exception as err:
            logging.error('Unable to perform action on relay: {}'.format(err))


def on_error(ws, error):
    logging.error(error)
    time.sleep(5)


def on_close(ws):
    logging.info("### closed ###")


def on_open(ws):
    logging.info('Opened connection...')

    def websocket_keepalive():
        send(ws, 'ping')

    Interval(20, websocket_keepalive)


def main():
    site_url = os.getenv('SITE_URL')
    grow_id = os.getenv('GROW_ID')
    sensor_id = os.getenv('SENSOR_ID')
    device_token = os.getenv('DEVICE_TOKEN')
    websocket_url = site_url.replace('https://', 'wss://').replace('http://', 'ws://')
    connection_url = '{}/ws/grows/{}/sensors/{}/'.format(websocket_url, grow_id, sensor_id)

    logging.info('-------------------------')
    logging.info('Gardeno - Device Software')
    logging.info('Site URL: {}'.format(site_url))
    logging.info('Grow ID: {}'.format(grow_id))
    logging.info('Sensor ID: {}'.format(sensor_id))
    logging.info('Connecting to: {}'.format(connection_url))

    while True:
        try:
            ws = websocket.WebSocketApp('{}?auth_token={}'.format(connection_url, device_token),
                                        on_message=on_message,
                                        on_error=on_error,
                                        on_close=on_close)
            ws.on_open = on_open
            ws.run_forever()
        except Exception as error:
            logging.error('Reconnecting because of error:')
            logging.error(error)
            time.sleep(5)


if __name__ == "__main__":
    main()
