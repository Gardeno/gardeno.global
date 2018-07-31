import greengrasssdk
from threading import Timer
import json
import os

client = greengrasssdk.client('iot-data')


def main():
    client.update_thing_shadow(thing_name='Foo', payload=json.dumps({"foo": "bar"}))
    Timer(5, main).start()


main()


# This is a dummy handler and will not be invoked
def function_handler(event, context):
    return
