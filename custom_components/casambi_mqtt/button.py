from custom_components.casambi_mqtt.entities.commands import PublishEntities
from homeassistant.components import mqtt
from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import CONF_NETWORK_NAME, DOMAIN, MQTT_TOPIC_PREFIX


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    network_name = hass.data[DOMAIN][CONF_NETWORK_NAME]
    async_add_entities([CasambiMqttReloadButton(hass, network_name)])


class CasambiMqttReloadButton(ButtonEntity):
    _mqtt_network_name: str

    def __init__(self, hass: HomeAssistant, network_name: str) -> None:
        self.hass = hass
        self._mqtt_network_name = network_name
        self._attr_name = "Reload Casambi entities"
        self._attr_unique_id = "casambi_mqtt_reload_entities"
        self._attr_icon = "mdi:cloud-download"

    async def async_press(self) -> None:
        await mqtt.async_publish(
            self.hass,
            f"{MQTT_TOPIC_PREFIX}/{self._mqtt_network_name}/commands",
            PublishEntities().to_json(),
        )
        self.async_write_ha_state()
