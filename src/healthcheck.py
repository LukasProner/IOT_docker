import json
import sys
import time
from loguru import logger
import paho.mqtt.client as mqtt

from models import Settings

settings = Settings()

# Globálne premenlivé
message_received = False
message_content = None


def on_connect(client: mqtt.Client, userdata, flags, reason_code, properties):
    """Callback pri pripojení k brokerovi."""
    logger.debug(f"Connected with result code {reason_code}")
    client.subscribe(f'{settings.base_topic}/status')


def on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
    """Callback pri prijatí správy."""
    global message_received, message_content
    logger.debug(f'{msg.topic}: {msg.payload}')
    message_content = json.loads(msg.payload.decode("utf-8"))
    message_received = True


def perform_healthcheck():
    """Hlavná funkcia na kontrolu stavu služby."""
    global message_received, message_content

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(settings.user, settings.password)

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        # Pripojenie k brokerovi
        client.connect(settings.broker, settings.port, 60)
        client.loop_start()

        logger.info("Čaká sa na správu zo služby...")

        # Čaká na správu s časovým limitom
        start_time = time.time()
        while time.time() - start_time < settings.healthcheck_timeout:
            if message_received:
                break
            time.sleep(0.1)

        client.loop_stop()
        client.disconnect()

        if not message_received:
            logger.error("Správa z témy /status nebola prijatá.")
            sys.exit(1)

        if message_content.get("status") != "online":
            logger.error(f"Stav služby nie je online: {message_content}")
            sys.exit(1)

        logger.info("Služba je online a funguje správne.")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Chyba počas healthchecku: {e}")
        sys.exit(1)


if __name__ == "__main__":
    perform_healthcheck()
