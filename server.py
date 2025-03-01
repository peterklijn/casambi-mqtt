import asyncio
import json
import logging
import os

import aiomqtt
import CasambiBt
from bleak import BLEDevice
from CasambiBt import Casambi, discover
from CasambiBt._unit import UnitControl as BtUnitControl
from CasambiBt._unit import UnitType as BtUnitType
from dotenv import load_dotenv

from custom_components.casambi_mqtt.entities.commands import (
    PublishEntities,
    SetLevel,
    SetScene,
    TurnOn,
)
from custom_components.casambi_mqtt.entities.entities import *

BROKER = "localhost"
PORT = 1883
TOPIC_PREFIX = "test/casambi"

load_dotenv()
LOG_LEVEL = os.getenv("LOG_LEVEL") or "INFO"
NETWORK_ADDRESS = os.getenv("CASAMBI_NETWORK_ADDRESS")
NETWORK_PASSWORD = os.getenv("CASAMBI_NETWORK_PASSWORD")
NETWORK_NAME = os.getenv("CASAMBI_NETWORK_NAME")
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(LOG_LEVEL)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
)
LOGGER.addHandler(handler)


async def log_exceptions(awaitable):
    try:
        return await awaitable
    except aiomqtt.MqttError as e:
        LOGGER.warning(f"Unhandled exception: {e}")


def to_unit_control_type(t: CasambiBt.UnitControlType) -> UnitControlType:
    return UnitControlType(t.name, t.value)


def to_unit_control(c: BtUnitControl) -> UnitControl:
    return UnitControl(
        c.default, c.length, c.offset, c.readonly, to_unit_control_type(c.type)
    )


def to_unit_type(t: BtUnitType) -> UnitType:
    return UnitType(
        t.id,
        t.manufacturer,
        t.mode,
        t.model,
        t.stateLength,
        [to_unit_control(c) for c in t.controls],
    )


def to_unit_state(s: CasambiBt.UnitState) -> UnitState:
    return UnitState(s.dimmer)


def to_entity(unit: CasambiBt.Unit) -> Unit:
    return Unit(
        unit.address,
        unit.deviceId,
        unit.is_on,
        unit.name,
        unit.online,
        to_unit_state(unit.state),
        unit.uuid,
        to_unit_type(unit.unitType),
    )


def to_scene(scene: CasambiBt.Scene) -> Scene:
    return Scene(scene.sceneId, scene.name)


async def process_command(
    message: aiomqtt.Message, casa: Casambi, client: aiomqtt.Client
) -> None:
    payload = message.payload.decode()
    command = json.loads(payload)
    match command["action"]:
        case SetLevel.ACTION:
            cmd = SetLevel.from_json(payload)
            unit = next(u for u in casa.units if u.address == cmd.address)
            await casa.setLevel(unit, cmd.value)
        case TurnOn.ACTION:
            cmd = TurnOn.from_json(payload)
            unit = next(u for u in casa.units if u.address == cmd.address)
            await casa.turnOn(unit)
        case PublishEntities.ACTION:
            for scene in casa.scenes:
                scene_entity = to_scene(scene)
                asyncio.create_task(
                    log_exceptions(
                        client.publish(
                            f"{TOPIC_PREFIX}/{NETWORK_NAME}/scenes/{scene_entity.scene_id}",
                            payload=scene_entity.to_json(),
                            retain=True,
                        )
                    )
                )
        case SetScene.ACTION:
            cmd = SetScene.from_json(payload)
            scene = next(s for s in casa.scenes if s.sceneId == cmd.scene_id)
            await casa.switchToScene(scene)


async def main() -> None:
    devices = await discover()
    device: BLEDevice | None = None
    for d in devices:
        if d.address == NETWORK_ADDRESS:
            device = d

    if device is None:
        LOGGER.info(
            "No casambi network specified, store the address of your network in CASAMBI_NETWORK_ADDRESS:"
        )
        for i, d in enumerate(devices):
            LOGGER.info(f"[{i}]\t{d.address}")
        exit(0)

    casa = Casambi()
    try:
        await casa.connect(device, NETWORK_PASSWORD)
        LOGGER.info("Connected to Casambi network")
        client = aiomqtt.Client(BROKER)
        interval = 5

        def callback(unit: CasambiBt.Unit) -> None:
            entity = to_entity(unit)
            asyncio.create_task(
                log_exceptions(
                    client.publish(
                        f"{TOPIC_PREFIX}/{NETWORK_NAME}/events/{unit.address}",
                        payload=entity.to_json(),
                        retain=True,
                    )
                )
            )

        while True:
            try:
                async with client:
                    await client.subscribe(f"{TOPIC_PREFIX}/{NETWORK_NAME}/commands")

                    casa.registerUnitChangedHandler(callback)

                    LOGGER.info(
                        "Subscribed to commands topic and UnitChangedHandler registered"
                    )
                    async for message in client.messages:
                        LOGGER.debug(
                            f"Received command: {message.payload.decode()} on topic: '{message.topic}'"
                        )
                        await process_command(message, casa, client)
            except aiomqtt.MqttError as e:
                LOGGER.warning(
                    f"Connection lost ({e}); Reconnecting in {interval} seconds ..."
                )
                casa.unregisterUnitChangedHandler(callback)
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                LOGGER.info("Main task cancelled, waiting for cleanup")
                break

    finally:
        LOGGER.info("Shutting down..")
        await casa.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
