import os
import time
import logging
from logging import StreamHandler
import json
from dotenv import load_dotenv
import adafruit_dht
from config import config
from utils.utils import connect_mqtt, publish, on_disconnect
from utils.constants import boardspins

load_dotenv()

app = config[os.getenv("ENVIRONMENT") or "default"]
logging.basicConfig(
    format="|%(asctime)s| [%(levelname)s] {%(module)s->%(funcName)s}: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %Z",
    level=app.LOGGING_LEVEL,
    handlers=[StreamHandler()],
)

def main():
    logging.info(f"rpi-dht service started, refresh time {app.READ_TIME} secs")
    client = connect_mqtt(app.MQTT_CLIENT_ID, app.MQTT_BROKER, int(app.MQTT_PORT), app.MQTT_USERNAME, app.MQTT_PASSWORD)
    client.loop_start()
    client.on_disconnect = on_disconnect
    pin = boardspins[f"D{app.DHT_PIN}"]
    sensor = adafruit_dht.DHT11(pin)
    while True:
        try:
            temperature = sensor.temperature
            humidity = sensor.humidity
            if humidity is not None and temperature is not None:
                logging.debug(f"Temp: {temperature:.2f} °C, Hum: {humidity:.2f} %")
                publish(client, app.MQTT_TOPIC, json.dumps({"temperature": temperature, "humidity": humidity}))
            else:
                logging.error("Failed reading DHT sensor")
        except RuntimeError as e:
            logging.error(f"Reading from DHT failure: {e.args[0]}")
            time.sleep(int(app.READ_TIME))
            continue
        except Exception as e:
            sensor.exit()
            raise e
        time.sleep(int(app.READ_TIME))
    client.loop_stop()

if __name__ == "__main__":
    main()
