# Raspberry Pi + DHT11 Sensor + MQTT

This project implements a simple temperature and humidity sensor using a Raspberry Pi and a DHT11 sensor. It uses [Adafruit DHT Library](https://github.com/adafruit/Adafruit_CircuitPython_DHT) to read the sensor data through One Wire protocol. It also sends the Temperature and Humidity to a MQTT Broker.

## Requirements
- Raspberry Pi 3, 4 or 5
- DHT11 or DHT22 Sensor
- i2c-tools, libgpiod2, libgpiod-dev and python3-libgpiod packages
- Docker and Docker Compose
- MQTT Broker

## Setup
- Install i2c-tools, libgpiod2, libgpiod-dev and python3-libgpiod
    ```bash
    sudo apt install -y i2c-tools libgpiod2 libgpiod-dev python3-libgpiod
    ```
- Reboot
    ```bash
    sudo reboot
    ```

- Check if gpio is available
    ```bash
    ls /dev/gpio*
    ```
    You should see the response
    ```bash
    /dev/gpiochip0 /dev/gpiochip1 /dev/gpiomem
    ```

- Create a `.env` file in the root of the project and add the following variables
    ```bash
    ENVIRONMENT=development
    READ_TIME=5
    DHT_PIN=17
    DHT_TYPE=DHT11
    MQTT_BROKER="localhost"
    MQTT_PORT=1883
    MQTT_TOPIC="/devices/CHANGE_DEVICE"
    MQTT_CLIENT_ID="rpi-user1"
    MQTT_USERNAME="CHANGE_USER"
    MQTT_PASSWORD="CHANGE_PASS"
    ```
    The `READ_TIME` parameter is in seconds and the `DHT_PIN` is the GPIO pin number where the sensor is connected.

- Compose the project
    ```bash
    docker compose up -p rpi-dht-mqtt --build -d
    ```