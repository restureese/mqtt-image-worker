from fastapi_mqtt.fastmqtt import FastMQTT
from fastapi import FastAPI
from fastapi_mqtt.config import MQTTConfig

from pydantic_settings import BaseSettings
from uuid import uuid4

import base64
import binascii


class Setting(BaseSettings):
    MQTT_HOST: str
    MQTT_USERNAME: str
    MQTT_PASSWORD: str
    MQTT_TOPIC: str
    MQTT_PORT: int

    class Config:
        env_file = ".env"
        case_sensitive = True


setting = Setting()

app = FastAPI()

mqtt_config = MQTTConfig(
    host=setting.MQTT_HOST,
    port=setting.MQTT_PORT,
    keepalive=60,
    username=setting.MQTT_USERNAME,
    password=setting.MQTT_PASSWORD,
    version=5.0

)

mqtt = FastMQTT(config=mqtt_config)

mqtt.init_app(app)


@mqtt.on_connect()
def connect(client, flags, rc, properties):
    mqtt.client.subscribe(setting.MQTT_TOPIC)  # subscribing mqtt topic
    print("Connected: ", client, flags, rc, properties)


@mqtt.on_message()
async def message(client, topic, payload, qos, properties):
    print("topic ", topic)
    try:
        image = base64.b64decode(payload.decode(), validate=True)
        file_to_save = f"{uuid4()}.png"
        with open(file_to_save, "wb") as f:
            f.write(image)
    except binascii.Error as e:
        print(e)


@mqtt.on_disconnect()
def disconnect(client, packet, exc=None):
    print("Disconnected")


@mqtt.on_subscribe()
def subscribe(client, mid, qos, properties):
    print("subscribed", client, mid, qos, properties)
