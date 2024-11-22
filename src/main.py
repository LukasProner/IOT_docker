import json
import sys
from functools import lru_cache

from apprise import Apprise
from loguru import logger
import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTMessage

from models import Notification, Settings

settings = Settings()
print(settings)


def handle_commands(client: mqtt.Client, message: dict):
    cmd = message.get("cmd")
    if 'cmd' in message and cmd == "shutdown":
        logger.info("Shutdown command received. Shutting down the service.")
        client.disconnect()
        sys.exit(0)
    else:
        logger.warning(f'Unknown command "{message["cmd"]}"')


def on_connect(client: mqtt.Client, userdata, flags, reason_code, properties):
    logger.debug(f"Connected with result code {reason_code}")
    client.subscribe(settings.base_topic)
    client.subscribe(f'{settings.base_topic}/cmd')
    client.publish(f'{settings.base_topic}/status', json.dumps({"status": "online"}), retain=True)


def on_message(client: mqtt.Client, userdata, msg: MQTTMessage):
    logger.debug(f'{msg.topic}: {msg.payload}')
    message = json.loads(msg.payload)

    if msg.topic.endswith('/cmd'):
        handle_commands(client, message)
    else:
        notify(message)


def notify(message: dict):
    logger.info('logged')

    # Notification(urls="xxx", title="alert". body
    notification = Notification(**message)

    apprise = Apprise()
    apprise.add(str(notification.urls))

    apprise.notify(
        body=notification.body,
        title=notification.title,
    )


def main():

    # username = settings.user
    # password = settings.password
    #
    # client = mqtt.Client()

    # if username and password:
    #     client.username_pw_set(username, password)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(settings.user, settings.password)
    client.will_set(f'{settings.base_topic}/status', json.dumps({"status": "offline"}), retain=True)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(settings.broker, settings.port, 60)

    logger.info('Waiting for messages.')
    client.loop_forever()


if __name__ == '__main__':
    main()
