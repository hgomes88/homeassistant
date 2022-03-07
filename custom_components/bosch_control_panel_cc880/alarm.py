"""Module that allows control and monitoring of an Alarm system
"""

import asyncio
from dataclasses import dataclass
from enum import Enum
import logging
from typing import Callable, Dict, List, Optional, Union
from aioretry import RetryInfo, retry

_LOGGER = logging.getLogger(__name__)


def to_hex(_bytes: Union[bytes, int]) -> str:
    """ Converts a single byte or a list of bytes into hex format

    Args:
        _bytes (bytes|int): Single byte or a list of bytes

    Returns:
        str: String representation of the byte(s) in hexadecimal format
    """

    _byte_str = ""
    if isinstance(_bytes, int):
        _bytes = bytes([_bytes])

    for _byte in _bytes:
        _byte_str += f"{int(_byte):02x}"
        _byte_str += " "
    return _byte_str


def to_bin(_bytes: Union[bytes, int]):
    """ Converts a single byte or a list of bytes into binary format

    Args:
        _bytes (bytes|int): Single byte or a list of bytes

    Returns:
        str: String representation of the byte(s) in binary format
    """
    _byte_str = ""
    if isinstance(_bytes, int):
        _bytes = bytes([_bytes])

    for _byte in _bytes:
        _byte_str += f"{int(_byte):08b}"
        _byte_str += " "
    return _byte_str


@dataclass
class Zone:
    """ Dataclass to store the zones of the alarm
    """

    number: int
    name: str = ""
    triggered = False


@dataclass
class Output:
    """Dataclass to store the varios alarm output states
    """

    number: int
    name: str = ""
    on = False


class ArmingMode(Enum):
    """Enumarator with all the alarm states
    """

    DISARMED = 0
    ARMED_AWAY = 1
    ARMED_STAY = 2


@dataclass
class Area:
    """Dataclass representig the alarm area
    """

    number: int
    name: str = ""
    mode: ArmingMode = ArmingMode.DISARMED


ZoneListener = Callable[[Zone], bool]
AreaListener = Callable[[Area], bool]
SirenListener = Callable[[bool], bool]


class Alarm:
    """Class representing the alarm object
    """

    NUMBER_OF_ZONES = 16
    # NUMBER_OF_AREAS = 4
    NUMBER_OF_AREAS = 1
    # NUMBER_OF_OUTPUTS = 6
    NUMBER_OF_OUTPUTS = 1
    MAX_PAR_REQUS = 1

    def __init__(
        self, ip: str, port: str, loop: Optional[asyncio.AbstractEventLoop] = None
    ) -> None:
        self._loop = loop or asyncio.get_event_loop()
        self._zone_listeners: Dict[int, List[ZoneListener]] = {}
        self._area_listeners: Dict[int, List[AreaListener]] = {}
        self._siren_listeners: List[SirenListener] = []
        self._zones: Dict[int, Zone] = {}
        self._num_par_reqs = 0
        self._ip = ip
        self._port = port

        self._create_outputs()
        self._create_areas()
        self._create_zones()
        self._siren = False
        self._reader: asyncio.StreamReader
        self._writer: asyncio.StreamWriter
        self._tasks: List[asyncio.Task] = []

    async def _open_connection(self):
        self._reader, self._writer = await asyncio.open_connection(self._ip, self._port)

    async def start(self) -> bool:
        """Establish the connection to the alarm
        """

        await self._open_connection()
        self._reader, self._writer = await asyncio.open_connection(self._ip, self._port)
        # Create the task that requests the status periodically
        self._tasks.append(asyncio.create_task(self._get_status_task()))
        return True

    async def stop(self) -> bool:
        """Stop the connection  to the alarm
        """

        for task in self._tasks:
            task.cancel()
        return True

    @property
    def zones(self):
        """Property that returns the list of zones available
        """

        return list(self._zones.values())

    def _create_zones(self):
        for i in range(self.NUMBER_OF_ZONES):
            zone = Zone(i + 1)
            self._zones[zone.number] = zone

    def _create_areas(self):
        self._areas: Dict[int, Area] = {}
        for i in range(self.NUMBER_OF_AREAS):
            area = Area(i + 1)
            self._areas[area.number] = area

    @property
    def areas(self):
        """Property that return the list of areas supported by the alarm
        """

        return self._areas

    @property
    def siren(self):
        """Property that return the siren status
        """

        return self._siren

    def _create_outputs(self):
        self._outputs: Dict[int, Output] = {}
        for i in range(self.NUMBER_OF_OUTPUTS):
            output = Output(i + 1)
            self._outputs[output.number] = output

    @staticmethod
    def _retry_policy(info: RetryInfo):
        if (
            isinstance(info.exception, asyncio.exceptions.TimeoutError)
            and info.fails <= 1
        ):
            return False, 4
        return True, 0

    async def _before_retry(self, info: RetryInfo) -> None:
        # Reconnect
        await self._open_connection()

    @retry(retry_policy="_retry_policy", before_retry="_before_retry")
    async def _send(self, message: bytes):

        # Send the command
        self._writer.write(message)
        await self._writer.drain()

        # Wait for a response
        return await asyncio.wait_for(self._reader.read(32), timeout=3)

    async def _send_command(self, message: bytes):
        resp = None

        while self._num_par_reqs >= self.MAX_PAR_REQUS:
            await asyncio.sleep(0.05)

        try:
            self._num_par_reqs += 1
            resp = await self._send(message)
        except asyncio.exceptions.TimeoutError:
            _LOGGER.warning("Message not received on time")
        except asyncio.IncompleteReadError as ex:
            _LOGGER.warning("Message not received. Reason: %s", ex)
        finally:
            self._num_par_reqs -= 1

        return resp

    async def _get_status_task(self):
        while True:
            _LOGGER.debug("Getting Status")
            await self.get_status_cmd()
            await asyncio.sleep(1)

    async def _handle_data(self, data: bytes):
        _LOGGER.debug("New Data: %s", to_hex(data))

        if self._is_status_msg(data):
            self._handle_status_msg(data)

    async def get_status_cmd(self):
        """Command to request the status of the alarm
        """

        cmd = bytes([0x01, 0x00, 0x00, 0x00, 0x91, 0x30, 0x19, 0x0F, 0x00, 0x00, 0xF1])
        resp = await self._send_command(cmd)
        if resp:
            _LOGGER.debug("Status Response: %s", resp)
            await self._handle_data(resp)

    @classmethod
    def _is_status_msg(cls, data: bytes):
        return data[:2] == bytes([0x04, 0x34])

    def _handle_status_msg(self, data: bytes):
        self._update_zone_status(data[3:5])
        self._update_siren_status(data[10])
        self._update_area_status(data[9])
        self._update_output_status(data[2])

    def _update_zone_status(self, data: bytes):
        for i in range(self.NUMBER_OF_ZONES):
            bit = i % 8
            byte = int(i / 8)
            status = bool(data[byte] & (1 << bit))
            zone = self._zones[i + 1]

            if zone.triggered != status:
                zone.triggered = status

                if zone.number in self._zone_listeners:
                    for listener in self._zone_listeners[zone.number]:
                        if listener:
                            asyncio.create_task(listener(zone))

                _LOGGER.info(
                    "Status of Zone %d changed to %d", zone.number, zone.triggered,
                )

    def add_zone_listener(self, zone_number: int, listener: ZoneListener):
        """Add a listener function to listen for zone state changes
        """

        if zone_number in set(self._zones.keys()):
            if zone_number not in self._zone_listeners:
                self._zone_listeners[zone_number] = []
            self._zone_listeners[zone_number].append(listener)

    def add_area_listener(self, area_number: int, listener: AreaListener):
        """Add a listener function to listen for are state changes
        """

        if area_number in set(self._areas.keys()):
            if area_number not in self._area_listeners:
                self._area_listeners[area_number] = []
            self._area_listeners[area_number].append(listener)

    def add_siren_listener(self, listener: SirenListener):
        """Add a listener function to listen for siren state changes
        """

        self._siren_listeners.append(listener)

    def _update_siren_status(self, data: int):
        bit = 6
        status = bool(data & (1 << bit))

        if self._siren != status:
            self._siren = status

            for listener in self._siren_listeners:
                if listener:
                    asyncio.create_task(listener(status))

            _LOGGER.info("Status of Siren changed to %d", self._siren)

    def _update_output_status(self, data: int):
        for i in range(self.NUMBER_OF_OUTPUTS):
            bit = i % 8
            status = bool(data & (1 << bit))
            out = self._outputs[i + 1]

            if out.on != status:
                out.on = status
                _LOGGER.info("The output %d changed to %d", out.number, out.on)

    def _update_area_status(self, data: int):

        for i in range(self.NUMBER_OF_AREAS):
            away_bit = i % 4
            stay_bit = away_bit + 4
            away_status = bool(data & (1 << away_bit))
            stay_status = bool(data & (1 << stay_bit))
            area = self._areas[i + 1]
            status_chanded = False

            if away_status and stay_status:
                _LOGGER.error(
                    "Both away and stay arming status not possible. Area %d",
                    area.number,
                )
            elif not away_status and not stay_status:
                if area.mode is not ArmingMode.DISARMED:
                    area.mode = ArmingMode.DISARMED
                    status_chanded = True
            elif away_status and area.mode is not ArmingMode.ARMED_AWAY:
                if area.mode is not ArmingMode.ARMED_AWAY:
                    status_chanded = True
                    area.mode = ArmingMode.ARMED_AWAY
            elif stay_status and area.mode is not ArmingMode.ARMED_STAY:
                if area.mode is not ArmingMode.ARMED_STAY:
                    status_chanded = True
                    area.mode = ArmingMode.ARMED_STAY
            if status_chanded:
                if area.number in self._area_listeners:
                    for listener in self._area_listeners[area.number]:
                        if listener:
                            asyncio.create_task(listener(area))
                _LOGGER.info("Status of Area %d changed to %s", area.number, area.mode)

    async def _get_crc(self, data: bytes):

        # TODO: For now we can have only static CRC
        if len(data) == 1:
            if data[0] in [0x00, 0x01]:
                return 0x16
            if data[0] in [0x02]:
                return 0x17
            if data[0] in [0x03, 0x04]:
                return 0x19
            if data[0] in [0x05]:
                return 0x1B
            if data[0] in [0x06, 0x07]:
                return 0x1C
            if data[0] in [0x08]:
                return 0x1D
            if data[0] in [0x09]:
                return 0x1F
            if data[0] in [0x1A]:
                return 0x2F
            if data[0] in [0x1B]:
                return 0x31

        return 0

    async def send_keys(self, keys: Union[str, List[str]]):
        """Simulates a keypad, allowing sending multiple keys
        """

        keys_list: List[str] = list(keys)

        new_keys: bytes = bytes([])

        for k in keys_list:
            if k.isdigit() and int(k) in range(0, 10):
                new_keys += bytes([int(k)])
            elif k == "*":
                new_keys += bytes([0x1B])
            elif k == "#":
                new_keys += bytes([0x1A])
            else:
                _LOGGER.error("Unrecognized key %s", k)
                return

        cmds = []
        max_keys = 1

        for i in range(0, len(new_keys), max_keys):
            cmds.append(new_keys[i : i + max_keys])

        for cmd in cmds:
            current_zone = bytes([1])
            n_keys = bytes([len(cmd)])
            _bytes = bytes.fromhex("0C00000000000000000000")
            _bytes = (
                _bytes[0:1]
                + cmd
                + _bytes[1 + len(cmd) : 8]
                + current_zone
                + n_keys
                + bytes([await self._get_crc(cmd)])
            )
            await self._send_command(_bytes)
