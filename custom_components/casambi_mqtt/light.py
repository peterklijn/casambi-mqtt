from typing import Any

from custom_components.casambi_mqtt.entities.commands import SetLevel, TurnOn
from homeassistant.components import mqtt
from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN, LIGHT_ADD_ENTITIES, MQTT_TOPIC_PREFIX
from .entities.entities import Unit


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    hass.data[DOMAIN][LIGHT_ADD_ENTITIES] = async_add_entities


class CasambiMqttLight(LightEntity):
    _attr_bt_address: str
    _mqtt_network_name: str

    def __init__(
        self, hass: HomeAssistant, topic: str, network_name: str, unit: Unit
    ) -> None:
        self.hass = hass
        self._mqtt_network_name = network_name
        self._attr_name = unit.name
        self._attr_unique_id = f"casambi_mqtt_light_{unit.address}"
        self._attr_is_on = unit.state.dimmer > 0
        self._attr_brightness = unit.state.dimmer
        self._attr_color_mode = ColorMode.BRIGHTNESS
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        self._topic = topic
        self._attr_bt_address = unit.address

    def update_entity(self, unit: Unit) -> None:
        self._attr_is_on = unit.state.dimmer > 0
        self._attr_brightness = unit.state.dimmer
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        if ATTR_BRIGHTNESS in kwargs:
            command = SetLevel(self._attr_bt_address, kwargs[ATTR_BRIGHTNESS])
        else:
            command = TurnOn(self._attr_bt_address)
        await mqtt.async_publish(
            self.hass,
            f"{MQTT_TOPIC_PREFIX}/{self._mqtt_network_name}/commands",
            command.to_json(),
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        command = SetLevel(self._attr_bt_address, 0)
        await mqtt.async_publish(
            self.hass,
            f"{MQTT_TOPIC_PREFIX}/{self._mqtt_network_name}/commands",
            command.to_json(),
        )
