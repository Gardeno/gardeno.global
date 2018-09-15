#!/usr/bin/env python3

import time
import logging

logging.basicConfig(level=logging.INFO)


def main():
    while True:
        logging.debug('Waiting for work.')
        time.sleep(5)


if __name__ == "__main__":
    main()
