from typing import Any

from homeassistant.components import mqtt
from homeassistant.components.scene import Scene as HAScene
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.casambi_mqtt.entities.commands import SetScene

from .const import DOMAIN, MQTT_TOPIC_PREFIX, SCENE_ADD_ENTITIES
from .entities.entities import Scene


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    hass.data[DOMAIN][SCENE_ADD_ENTITIES] = async_add_entities


class CasambiMqttScene(HAScene):
    _attr_casambi_id: int
    _mqtt_network_name: str

    def __init__(self, hass: HomeAssistant, network_name: str, scene: Scene) -> None:
        self.hass = hass
        self._mqtt_network_name = network_name
        self._attr_casambi_id = scene.scene_id
        self._attr_unique_id = f"casambi_mqtt_scene_{scene.scene_id}"
        self._attr_name = scene.name
        self._attr_icon = "mdi:lamps"

    @property
    def name(self) -> str:
        return self._attr_name

    def update_entity(self, scene: Scene) -> None:
        self._attr_name = scene.name
        self.async_write_ha_state()

    async def async_activate(self, **kwargs: Any) -> None:
        command = SetScene(self._attr_casambi_id)
        await mqtt.async_publish(
            self.hass,
            f"{MQTT_TOPIC_PREFIX}/{self._mqtt_network_name}/commands",
            command.to_json(),
        )
