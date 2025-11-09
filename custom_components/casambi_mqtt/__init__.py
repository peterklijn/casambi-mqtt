from homeassistant.components.mqtt import ReceiveMessage, async_subscribe
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_NETWORK_NAME,
    DEFAULT_NETWORK_NAME,
    DOMAIN,
    LIGHT_ADD_ENTITIES,
    LOGGER,
    MQTT_TOPIC_PREFIX,
    SCENE_ADD_ENTITIES,
)
from .entities.entities import Scene, Unit
from .light import CasambiMqttLight
from .scene import CasambiMqttScene

PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.BUTTON, Platform.SCENE]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """YAML setup (unused)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][LIGHT_ADD_ENTITIES] = None
    hass.data[DOMAIN][SCENE_ADD_ENTITIES] = None

    network_name = entry.options.get(
        CONF_NETWORK_NAME, entry.data.get(CONF_NETWORK_NAME, DEFAULT_NETWORK_NAME)
    )

    hass.data[DOMAIN][CONF_NETWORK_NAME] = network_name

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def event_processor(msg: ReceiveMessage) -> None:
        try:
            unit = Unit.from_json(msg.payload)
        except ValueError:
            LOGGER.warning(
                f"Invalid payload received for event, payload: {msg.payload}, "
                f"topic: {msg.topic}"
            )
            return

        if unit.type() != Unit.TYPE_LIGHT:
            LOGGER.debug(
                f"Received msg from {unit.name} which is not a light "
                f"(it is {unit.type()}). Ignoring.."
            )
            return

        async_add_entities = hass.data[DOMAIN][LIGHT_ADD_ENTITIES]
        if async_add_entities is None:
            LOGGER.warning("Light platform not ready yet. Message ignored..")
            return

        if msg.topic not in hass.data[DOMAIN]:
            LOGGER.debug(
                f"New Casambi light detected on topic {msg.topic}, "
                f"creating light {unit.name} with state {unit.state.dimmer}"
            )
            light_entity = CasambiMqttLight(hass, msg.topic, network_name, unit)
            hass.data[DOMAIN][msg.topic] = light_entity
            async_add_entities([light_entity])
        else:
            LOGGER.debug(
                f"Updating existing light for topic {msg.topic}, "
                f"updating light {unit.name} with state {unit.state.dimmer}"
            )
            light_entity: CasambiMqttLight = hass.data[DOMAIN][msg.topic]
            light_entity.update_entity(unit)

    async def scene_processor(msg: ReceiveMessage) -> None:
        try:
            scene = Scene.from_json(msg.payload)
        except ValueError:
            LOGGER.warning(
                f"Invalid payload received for scene, payload: {msg.payload}, "
                f"topic: {msg.topic}"
            )
            return

        async_add_entities = hass.data[DOMAIN][SCENE_ADD_ENTITIES]
        if async_add_entities is None:
            LOGGER.warning("Scene platform not ready yet. Message ignored..")
            return

        if msg.topic not in hass.data[DOMAIN]:
            LOGGER.debug(
                f"New MQTT Scene detected: {msg.topic}, creating scene {scene.name}"
            )
            scene_entity = CasambiMqttScene(hass, network_name, scene)
            hass.data[DOMAIN][msg.topic] = scene_entity
            async_add_entities([scene_entity])
        else:
            LOGGER.debug(
                f"Updating existing scene for topic: {msg.topic}, "
                f"Updating scene {scene.name} (id {scene.scene_id})"
            )
            scene_entity: CasambiMqttScene = hass.data[DOMAIN][msg.topic]
            scene_entity.update_entity(scene)

    await async_subscribe(
        hass, f"{MQTT_TOPIC_PREFIX}/{network_name}/events/#", event_processor, 1
    )
    await async_subscribe(
        hass, f"{MQTT_TOPIC_PREFIX}/{network_name}/scenes/#", scene_processor, 1
    )
    LOGGER.debug("Casambi MQTT subscriptions set up for events and scenes")

    return True
