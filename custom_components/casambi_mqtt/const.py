from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "casambi_mqtt"
LIGHT_ADD_ENTITIES = "light_add_entities"
SCENE_ADD_ENTITIES = "scene_add_entities"

MQTT_TOPIC_PREFIX = "casambi"
CONF_NETWORK_NAME = "mqtt_network_name"
DEFAULT_NETWORK_NAME = "default"
