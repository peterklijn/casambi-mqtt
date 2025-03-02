# Home Assistant integration for Casambi using MQTT

This is a Home Assistant integration for Casambi networks. It uses the 
[unofficial Casambi Bluetooth](https://github.com/lkempf/casambi-bt)
library, but unlike the [Casambi Bluetooth HA integration](https://github.com/lkempf/casambi-bt-hass/)
from the same author as the library, it introduces MQTT as a middleman between the library and Home Assistant.
This allows you to run the library on a different device than Home Assistant.

## Why?

Because the device where I run Home Assistant on does not have Bluetooth :)

Does your Home Assistant hardware have bluetooth? Then you're probably better off with the
[Casambi Bluetooth HA integration](https://github.com/lkempf/casambi-bt-hass/), as this version is
very limited. For now, it only supports dimmable lights, and scenes.


This is simple, by having custom_components look (README + structure) the same
it is easier for developers to help each other and for users to start using them.

If you are a developer and you want to add things to this "blueprint" that you think more
developers will have use for, please open a PR to add it :)

## Setup

In addition to running this integration in Home Assistant, you need to have the following:

- An MQTT Server
- The [MQTT integration](https://www.home-assistant.io/integrations/mqtt/) installed and configured in Home Assistant
- The [server](./server.py) running somewhere with Bluetooth

Copy the `.env.example` to `.env` and fill in the required fields. Don't know the Casambi Bluetooth address? 
Run the server and it will list all Casambi networks. 

### Running the server with docker

```yaml
services:
  casambi-server:
    image: peterklijn/casambi-mqtt-server:0.0.1
    environment:
      MQTT_BROKER: "<broker address>"
      MQTT_USERNAME: "<optional broker username, or remove line>"
      MQTT_PASSWORD: "<optional broker password, or remove line>"
      CASAMBI_NETWORK_ADDRESS: "<casambi bluetooth address>"
      CASAMBI_NETWORK_PASSWORD: "<casambi password>"
      CASAMBI_NETWORK_NAME: "<optional network name, used in mqtt topic>"
    privileged: true
    network_mode: host
    volumes:
      - /var/run/dbus:/var/run/dbus
```

## Local development

1. `docker compose up -d`
2. Initialize Home Assistant, visit http://localhost:8123, create a user
3. Install the MQTT integration: On the [integration page](http://localhost:8123/config/integrations/dashboard) add the integration 'MQTT'
4. Connect to the broker, hostname = 'mosquitto'
5. Install HACS, follow the instructions mentioned [here](https://www.hacs.xyz/docs/use/download/download/#to-download-hacs-container), connect to the container using `docker exec -ti casambi-mqtt-homeassistant-1 bash`