#!/usr/bin/env python3

import time
import logging
import sys
import os
import signal
from Adafruit_SHT31 import *
from dotenv import load_dotenv
from pathlib import Path
import websocket

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


def signal_handler(sig, frame):
    logging.info('Exiting...')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def on_message(ws, message):
    logging.info('Received message: {}'.format(message))
    logging.info(message)


def on_error(ws, error):
    logging.error(error)
    time.sleep(5)


def on_close(ws):
    logging.info("### closed ###")


def on_open(ws):
    '''
    def run(*args):
        for i in range(3):
            time.sleep(1)
            ws.send("Hello %d" % i)
        time.sleep(1)
        ws.close()
        print("thread terminating...")
    thread.start_new_thread(run, ())
    '''
    logging.info('Opened connection...')


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
