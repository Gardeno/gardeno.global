#!/usr/bin/env python3

import time
import logging
import sys
from Adafruit_SHT31 import *

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


def main():
    logging.info('Starting!')
    while True:
        logging.info('Waiting for work.')
        time.sleep(5)


if __name__ == "__main__":
    main()
