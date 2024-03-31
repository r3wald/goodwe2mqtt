import asyncio
import goodwe
import influxdb_client
import pprint
import time
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import dotenv_values
from paho.mqtt import client as mqtt_client


def connect_mqtt(config):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client_id = config['MQTT_CLIENT_ID']
    username = config['MQTT_USERNAME']
    password = config['MQTT_PASSWORD']
    host = config['MQTT_HOST']
    port = int(config['MQTT_PORT'])

    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(host, port)
    return client


def send_data_to_mqtt(config, values):
    client = connect_mqtt(config)
    keys = ['battery_soc', 'ppv', 'grid_mode', 'grid_mode_label', 'grid_in_out', 'grid_in_out_label']
    #pprint.pprint(values)
    for key in values:
        if key not in keys:
            continue
        topic = f"goodwe/{key}"
        print(f"{topic}: {values[key]}")
        client.publish(topic, str(values[key]))


def send_data_to_influxdb(config, influxdbWriteApi, values):
    for key in values:
        p = influxdb_client.Point(key).field("value", values[key])
        influxdbWriteApi.write(bucket=config['INFLUXDB_BUCKET'], org=config['INFLUXDB_ORG'], record=p)


async def get_runtime_data(config, influxdbWriteApi):
    inverter = await goodwe.connect(config['GOODWE_IP'])
    runtime_data = await inverter.read_runtime_data()
    sensors = inverter.sensors()
    values = {}
    for sensor in inverter.sensors():
        if sensor.id_ in runtime_data:
            if sensor.id_ == 'timestamp':
                continue
            values[sensor.id_] = runtime_data[sensor.id_]
    #print(f"{time.asctime(time.localtime(time.time()))} | solar power: {runtime_data['ppv']}")
    #pprint.pprint(values)
    send_data_to_influxdb(config, influxdbWriteApi, values)
    send_data_to_mqtt(config, values)


async def init(config):
    print(f"================================================================================")
    print(f"Starting goodwe2mqtt")
    print("Available sensors:")
    inverter = await goodwe.connect(config['GOODWE_IP'])
    for sensor in inverter.sensors():
        # pp.pprint(sensor)
        print(f"{sensor.id_}: {sensor.name} in {sensor.unit}")
    print(f"--------------------------------------------------------------------------------")


config = dotenv_values(".env")
pp = pprint.PrettyPrinter(indent=4)
influxdb = influxdb_client.InfluxDBClient(
    url=config['INFLUXDB_URL'],
    token=config['INFLUXDB_TOKEN'],
    org=config['INFLUXDB_ORG'],
)
influxdbWriteApi = influxdb.write_api(write_options=SYNCHRONOUS)

asyncio.run(init(config))
while True:
    asyncio.run(get_runtime_data(config, influxdbWriteApi))
    time.sleep(60)
