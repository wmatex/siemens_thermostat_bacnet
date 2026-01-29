import asyncio
import os

from enum import IntEnum
from struct import pack, unpack
from typing import Any, Dict, List, Optional, Tuple

DEBUG = os.getenv("DEBUG") is not None


class APDUType(IntEnum):
    CONFIRMED_REQ = 0
    UNCONFIRMED_REQ = 1
    SIMPLE_ACK = 2
    COMPLEX_ACK = 3
    SEGMENT_ACK = 4


class PDUFlags(IntEnum):
    SEGMENTED_RESPONSE_ACCEPTED = 2
    MORE_SEGMENTS = 4
    SEGMENTED_REQUEST = 8


# max 16 segments
MAX_RESPONSE_SEGMENTS = 4

# max 1024 octets
MAX_APDU_SIZE = 4

# use static invoke ID
INVOKE_ID = 1

TAG_OBJECT_TYPE_SHIFT = 22
TAG_INSTANCE_ID_MASK = 0x3FFFFF

TAG_OPEN = 6
TAG_CLOSE = 7
TAG_NO_PROPERTY_VALUE = 4
TAG_NO_PROPERTY_ACCESS_ERROR = 5

PROPERTY_ACCESS_ERROR_SIZE = 4


class ServiceChoice(IntEnum):
    READ_PROPERTY_MULTIPLE = 14
    WRITE_PROPERTY = 15


class UnconfirmedServiceChoice(IntEnum):
    UNCONFIRMED_PRIVATE_TRANSFER = 4


BVLC_TYPE = 0x81
BVLC_FUNCTION_UNICAST = 0x0A
BVLC_FUNCTION_BROADCAST = 0x0B
BVLC_LENGTH = 4

NPDU_VERSION = 1
NPDU_EXPECT_REPLY = 4
NPDU = pack("!BB", NPDU_VERSION, NPDU_EXPECT_REPLY)


class ReadValue(IntEnum):
    DESCRIPTION = 28
    OBJECT_NAME = 77
    PRESENT_VALUE = 85
    PRIORITY_ARRAY = 87


class ObjectType(IntEnum):
    ANALOG_INPUT = 0
    ANALOG_OUTPUT = 1
    ANALOG_VALUE = 2
    BINARY_INPUT = 3
    BINARY_VALUE = 5
    DEVICE = 8
    MULTI_STATE_VALUE = 19
    POSITIVE_INTEGER_VALUE = 48


# ObjectIdentifier tuple represents ObjectType and InstanceIdentifier
ObjectIdentifier = Tuple[ObjectType, int]

# ObjectProperties represents a map of ReadValue to the actual value
ObjectProperties = List[Tuple[ReadValue, Any]]

DeviceState = Dict[ObjectIdentifier, ObjectProperties]


class Tag:
    def __init__(self, number: int, is_context: bool, length_type: int):
        self.number = number
        self.is_context = is_context
        self.length_type = length_type

    @property
    def int(self) -> int:
        ctx = 8 if self.is_context else 0
        return self.number << 4 | ctx | self.length_type

    def pack(self) -> bytes:
        return pack("!B", self.int)


class CtxTag(Tag):
    def __init__(self, number: int, length_type: int):
        super().__init__(number=number, is_context=True, length_type=length_type)


class AppTag(Tag):
    def __init__(self, number: int, length_type: int):
        super().__init__(number=number, is_context=False, length_type=length_type)


class WriteType(IntEnum):
    UnsignedInt = 2
    Real = 4
    Enumerated = 9


class DecodingError(Exception):
    pass


class DeviceProperty:
    def __init__(
        self,
        object_type: ObjectType,
        instance_id: int,
        read_values: Optional[List[ReadValue]] = None,
        priority: Optional[int] = None,
        write_type: Optional[WriteType] = None,
    ):
        self.object_type = object_type
        self.instance_id = instance_id
        self.read_values = read_values or [ReadValue.PRESENT_VALUE]
        self.priority = priority
        self.write_type = write_type

    @property
    def object_identifier(self) -> ObjectIdentifier:
        return (self.object_type, self.instance_id)

    def apdu_object_identifier(self) -> bytes:
        apdu = CtxTag(0, 4).pack()
        apdu += pack("!I", self.object_type << TAG_OBJECT_TYPE_SHIFT | self.instance_id)
        return apdu

    # read_access_spec returns APDU's read access spec for read-property-multiple service
    def read_access_spec(self) -> bytes:
        # object-identifier definition
        apdu = self.apdu_object_identifier()

        # list of property references
        apdu += CtxTag(1, TAG_OPEN).pack()

        for read_value in self.read_values:
            apdu += pack("!BB", CtxTag(0, 1).int, read_value)

        apdu += CtxTag(1, TAG_CLOSE).pack()

        return apdu

        # read_access_spec returns APDU's read access spec for read-property-multiple service

    def write_access_spec(self, value: Any) -> bytes:
        # object-identifier definition
        apdu = self.apdu_object_identifier()
        apdu += pack("!BB", CtxTag(1, 1).int, ReadValue.PRESENT_VALUE)

        apdu += CtxTag(3, TAG_OPEN).pack()

        if value is None:
            apdu += AppTag(0, 0).pack()
        elif self.object_type == ObjectType.ANALOG_VALUE:
            apdu += pack("!Bf", AppTag(WriteType.Real, 4).int, value)
        elif self.object_type == ObjectType.BINARY_VALUE:
            apdu += pack("!BB", AppTag(WriteType.Enumerated, 1).int, value)
        else:
            apdu += pack("!BB", AppTag(WriteType.UnsignedInt, 1).int, value)

        apdu += CtxTag(3, TAG_CLOSE).pack()

        if self.priority is not None:
            apdu += pack("!BB", CtxTag(4, 1).int, self.priority)

        return apdu


# _read_property_multiple returns request payload for read-property-multiple service
def _read_property_multiple(device_properties: List[DeviceProperty]) -> bytes:
    apdu = pack(
        "!BBBB",
        APDUType.CONFIRMED_REQ << 4 | PDUFlags.SEGMENTED_RESPONSE_ACCEPTED,
        MAX_RESPONSE_SEGMENTS << 4 | MAX_APDU_SIZE,
        INVOKE_ID,
        ServiceChoice.READ_PROPERTY_MULTIPLE,
    )

    # for each device property, build read access spec chunk and append to the APDU
    for dp in device_properties:
        apdu += dp.read_access_spec()

    bvlc = pack(
        "!BBH", BVLC_TYPE, BVLC_FUNCTION_UNICAST, BVLC_LENGTH + len(NPDU) + len(apdu)
    )

    return bvlc + NPDU + apdu


# _parse_read_property_multiple_response and return DeviceState
def _parse_read_property_multiple_response(response: bytes) -> DeviceState:
    bvlc_type, bvlc_function, _ = unpack("!BBH", response[0:4])
    if bvlc_type != BVLC_TYPE or bvlc_function != BVLC_FUNCTION_UNICAST:
        raise DecodingError("unexpected response")

    apdu_start_index = BVLC_LENGTH + len(NPDU)
    apdu = response[apdu_start_index:]

    apdu_type = apdu[0] >> 4

    if apdu_type != APDUType.COMPLEX_ACK:
        raise DecodingError(f"unsupported response type: {apdu_type}")

    invoke_id = apdu[1]
    if invoke_id != INVOKE_ID:
        raise DecodingError(f"unexpected invoke ID: {invoke_id}")

    service_choice = apdu[2]
    if service_choice != ServiceChoice.READ_PROPERTY_MULTIPLE:
        raise DecodingError(f"unexpected service choice: {service_choice}")

    decoder = BACnetDecoder(apdu, 3)

    device_state = {}

    while not decoder.eof():
        object_type, instance_number = decoder.parse_object_identifier()
        object_id = (object_type, instance_number)
        device_state[object_id] = decoder.parse_list_of_results()

    return device_state


def _segment_ack(invoke_id: int, sequence_number: int, window_size: int) -> bytes:
    apdu = pack(
        "!BBBB",
        APDUType.SEGMENT_ACK << 4,
        invoke_id,
        sequence_number,
        window_size,
    )

    bvlc = pack(
        "!BBH", BVLC_TYPE, BVLC_FUNCTION_UNICAST, BVLC_LENGTH + len(NPDU) + len(apdu)
    )

    return bvlc + NPDU + apdu


PRIORITY_ARRAY_PROPERTY_ID = 87  # BACnet Priority_Array property identifier


class BACnetDecoder:
    def __init__(self, data: bytes, offset: int = 0):
        self.data = data
        self.i = offset

    def eof(self) -> bool:
        return self.i >= len(self.data)

    def read_bytes(self, n: int) -> bytes:
        if self.i + n > len(self.data):
            raise DecodingError("unexpected EOF")

        data = self.data[self.i : self.i + n]
        self.i += n
        return data

    def read_byte(self) -> int:
        if self.i + 1 > len(self.data):
            raise DecodingError("unexpected EOF")

        byte = self.data[self.i]
        self.i += 1
        return byte

    def peek_tag(self) -> Tuple[int, int, int]:
        """Peek next tag without consuming it."""
        saved = self.i
        try:
            return self.read_tag()
        finally:
            self.i = saved

    # read_tag returns tag number, class and type/length.
    # NOTE: In BACnet, tag_class=0 -> application tag, tag_class=1 -> context tag
    def read_tag(self) -> Tuple[int, int, int]:
        byte = self.read_byte()

        tag_number = byte >> 4
        tag_class = (byte >> 3) & 1
        tag_type_length = byte & 7

        # extended length (basic form only; your existing code)
        if tag_type_length == 5:
            tag_type_length = self.read_byte()

        return tag_number, tag_class, tag_type_length

    def read_context_tag(self) -> Tuple[int, int]:
        tag_number, tag_class, tag_type_length = self.read_tag()
        if tag_class != 1:
            raise DecodingError(f"expected context specific tag, got {tag_class}")
        return tag_number, tag_type_length

    def read_application_tag(self) -> Tuple[int, int]:
        tag_number, tag_class, tag_type_length = self.read_tag()
        if tag_class != 0:
            raise DecodingError(f"expected application tag, got {tag_class}")
        return tag_number, tag_type_length

    def parse_object_identifier(self) -> Tuple["ObjectType", int]:
        tag_number, tag_length = self.read_context_tag()
        if tag_number != 0:
            raise DecodingError("unexpected tag")

        data = unpack("!I", self.read_bytes(tag_length))[0]
        object_type = ObjectType(data >> TAG_OBJECT_TYPE_SHIFT)
        instance_number = data & 0x3FFFFF
        return object_type, instance_number

    def parse_list_of_results(self) -> "ObjectProperties":
        opening_tag_number, tag_type = self.read_context_tag()
        if tag_type != TAG_OPEN:
            raise DecodingError("expected opening tag")

        results = []

        while True:
            tag_number, tag_type = self.read_context_tag()
            if tag_number == opening_tag_number and tag_type == TAG_CLOSE:
                break

            if tag_number != 2:
                raise DecodingError("unexpected tag")

            prop_id = self.read_byte()
            read_value = ReadValue(prop_id)

            # pass property id so read_value can decode Priority_Array specially
            value = self.read_value(property_id=prop_id)

            results.append((read_value, value))

        return results

    def read_value(self, property_id: int | None = None) -> Any:
        # check the opening tag
        opening_tag_number, tag_type = self.read_context_tag()
        if tag_type != TAG_OPEN:
            raise DecodingError("expected opening tag")

        value: Any = 0

        if opening_tag_number == TAG_NO_PROPERTY_VALUE:
            # Priority_Array (87) is an array of 16 PriorityValue elements
            if property_id == PRIORITY_ARRAY_PROPERTY_ID:
                value = self.parse_priority_array(opening_tag_number)
            else:
                tag_number, tag_length = self.read_application_tag()
                value = self.parse_value_element(tag_number, tag_length)

        elif opening_tag_number == TAG_NO_PROPERTY_ACCESS_ERROR:
            self.read_bytes(PROPERTY_ACCESS_ERROR_SIZE)

        # check the closing tag
        tag_number, tag_type = self.read_context_tag()
        if tag_number != opening_tag_number or tag_type != TAG_CLOSE:
            raise DecodingError("expected closing tag")

        return value

    def parse_value_element(self, tag_number: int, tag_len_or_val: int) -> Any:
        # 0 = NULL (no content)
        if tag_number == 0:
            # NULL should have no content bytes
            if tag_len_or_val:
                self.read_bytes(tag_len_or_val)
            return None

        # 1 = BOOLEAN: boolean value is encoded in the LVT bits (0/1), no content bytes
        if tag_number == 1:
            return bool(tag_len_or_val)

        # 2 = Unsigned Integer
        if tag_number == 2:
            return self.parse_unsinged_int(tag_len_or_val)

        # 3 = Signed Integer (2's complement)
        if tag_number == 3:
            return self.parse_signed_int(tag_len_or_val)

        # 4 = Real (IEEE-754 float)
        if tag_number == 4:
            return self.parse_float(tag_len_or_val)

        # 5 = Double (IEEE-754 double)
        if tag_number == 5:
            return self.parse_double(tag_len_or_val)

        # 7 = Character String
        if tag_number == 7:
            return self.parse_string(tag_len_or_val)

        # 9 = Enumerated
        if tag_number == 9:
            return self.parse_enumarated_value(tag_len_or_val)

        # 12 = Object Identifier (application-tagged)
        if tag_number == 12:
            return self.parse_application_object_identifier(tag_len_or_val)

        # Fallback: unknown/unsupported element type
        raw = self.read_bytes(tag_len_or_val)
        return {"tag": tag_number, "raw": raw}

    def parse_priority_array(self, opening_tag_number: int) -> list[Any]:
        """
        Decode BACnet Priority_Array payload (inside propertyValue opening/closing context tag).

        The payload is a sequence of 16 application-tagged PriorityValue elements,
        terminated by the closing context tag.
        """
        values: list[Any] = []

        while True:
            # stop when the next tag is the closing context tag for the propertyValue wrapper
            tnum, tclass, tlvt = self.peek_tag()
            if tclass == 1 and tnum == opening_tag_number and tlvt == TAG_CLOSE:
                break

            # otherwise next must be an application tag element
            app_tag, app_len_or_val = self.read_application_tag()
            values.append(self.parse_value_element(app_tag, app_len_or_val))

        return values

    # ----------------------------
    # Primitive parsers (some improved)
    # ----------------------------

    def parse_enumarated_value(self, length: int) -> int:
        # enumerated can be 1..4 bytes; decode big-endian like unsigned
        value = 0
        for _ in range(length):
            value = (value << 8) | self.read_byte()
        return value

    def parse_unsinged_int(self, length: int) -> int:
        value = 0
        for _ in range(length):
            value = (value << 8) | self.read_byte()
        return value

    def parse_signed_int(self, length: int) -> int:
        # big-endian two's complement
        raw = int.from_bytes(self.read_bytes(length), byteorder="big", signed=False)
        sign_bit = 1 << (length * 8 - 1)
        return raw - (1 << (length * 8)) if (raw & sign_bit) else raw

    def parse_float(self, length: int) -> float:
        if length != 4:
            raise DecodingError(f"unsupported float size: {length}")
        return unpack("!f", self.read_bytes(length))[0]

    def parse_double(self, length: int) -> float:
        if length != 8:
            raise DecodingError(f"unsupported double size: {length}")
        return unpack("!d", self.read_bytes(length))[0]

    def parse_string(self, length: int) -> str:
        encoding = self.read_byte()
        if encoding != 0:
            raise DecodingError(f"unsupported encoding: {encoding}")
        return self.read_bytes(length - 1).decode("utf-8")

    def parse_application_object_identifier(
        self, length: int
    ) -> Tuple["ObjectType", int]:
        if length != 4:
            raise DecodingError(f"unsupported object identifier size: {length}")
        data = unpack("!I", self.read_bytes(length))[0]
        object_type = ObjectType(data >> TAG_OBJECT_TYPE_SHIFT)
        instance_number = data & 0x3FFFFF
        return object_type, instance_number


def _write_property(device_property: DeviceProperty, value: Any) -> bytes:
    apdu = pack(
        "!BBBB",
        APDUType.CONFIRMED_REQ << 4 | PDUFlags.SEGMENTED_RESPONSE_ACCEPTED,
        MAX_RESPONSE_SEGMENTS << 4 | MAX_APDU_SIZE,
        INVOKE_ID,
        ServiceChoice.WRITE_PROPERTY,
    )

    apdu += device_property.write_access_spec(value)

    bvlc = pack(
        "!BBH", BVLC_TYPE, BVLC_FUNCTION_UNICAST, BVLC_LENGTH + len(NPDU) + len(apdu)
    )

    return bvlc + NPDU + apdu


# _parse_write_property_response and check for errors
def _parse_write_property_response(response: bytes):
    bvlc_type, bvlc_function, _ = unpack("!BBH", response[0:4])
    if bvlc_type != BVLC_TYPE or bvlc_function != BVLC_FUNCTION_UNICAST:
        raise DecodingError("unexpected response")

    apdu = response[BVLC_LENGTH + len(NPDU) :]

    apdu_type = apdu[0] >> 4

    if apdu_type != APDUType.SIMPLE_ACK:
        raise DecodingError(f"unsupported response type: {apdu_type}")

    invoke_id = apdu[1]
    if invoke_id != INVOKE_ID:
        raise DecodingError(f"unexpected invoke ID: {invoke_id}")

    service_choice = apdu[2]
    if service_choice != ServiceChoice.WRITE_PROPERTY:
        raise DecodingError(f"unexpected service choice: {service_choice}")


DEFAULT_BACNET_PORT = 47808


class BACnetRequest(asyncio.DatagramProtocol):
    _transport: asyncio.DatagramTransport

    # response is the response payload
    response: bytes

    # exception is the exception that occurred during the request
    exception: Exception | None

    def __init__(self, request: bytes, done: asyncio.Future | None = None):
        self.request = request

        if done is None:
            done = asyncio.get_running_loop().create_future()

        self.done = done

    def connection_made(self, transport: asyncio.DatagramTransport):
        self._transport = transport
        self._transport.sendto(self.request)

    def datagram_received(self, data: bytes, addr: Tuple[str, int]):
        self.response = data
        self._transport.close()

    def error_received(self, exc: Exception):
        self.exception = exc

    def connection_lost(self, exc: Exception | None):
        self.exception = exc
        self.done.set_result(True)

    def wait(self, timeout: float = 1.0):
        return asyncio.wait_for(self.done, timeout=timeout)


class _BACnetSegmentedProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        self.queue: asyncio.Queue[bytes] = asyncio.Queue()
        self._transport: asyncio.DatagramTransport | None = None
        self.exception: Exception | None = None

    def connection_made(self, transport: asyncio.DatagramTransport):
        self._transport = transport

    def datagram_received(self, data: bytes, addr: Tuple[str, int]):
        self.queue.put_nowait(data)

    def error_received(self, exc: Exception):
        self.exception = exc

    def connection_lost(self, exc: Exception | None):
        self.exception = exc

    async def receive(self, timeout: float = 1.0) -> bytes:
        return await asyncio.wait_for(self.queue.get(), timeout=timeout)


class BACnetClient:
    def __init__(self, address: str, port: int = DEFAULT_BACNET_PORT):
        self.address = address
        self.port = port

    async def _send(self, request: bytes) -> bytes:
        loop = asyncio.get_running_loop()

        bacnet_request = BACnetRequest(request)

        transport, _ = await loop.create_datagram_endpoint(
            lambda: bacnet_request, remote_addr=(self.address, self.port)
        )

        try:
            await bacnet_request.wait(timeout=1.0)
        finally:
            transport.close()

        if bacnet_request.exception is not None:
            raise ConnectionError from bacnet_request.exception

        return bacnet_request.response

    async def read_multiple(
        self, device_properties: List[DeviceProperty]
    ) -> DeviceState:
        request = _read_property_multiple(device_properties)

        if DEBUG:
            print(f">>> {request.hex()}")

        loop = asyncio.get_running_loop()
        protocol = _BACnetSegmentedProtocol()
        transport, _ = await loop.create_datagram_endpoint(
            lambda: protocol, remote_addr=(self.address, self.port)
        )

        try:
            transport.sendto(request)

            response = await protocol.receive(timeout=1.0)
            if protocol.exception is not None:
                raise ConnectionError from protocol.exception

            if DEBUG:
                print(f"<<< {response.hex()}")

            apdu_start_index = BVLC_LENGTH + len(NPDU)
            apdu = response[apdu_start_index:]
            apdu_type = apdu[0] >> 4
            segmented = apdu_type == APDUType.COMPLEX_ACK and (
                apdu[0] & (PDUFlags.SEGMENTED_REQUEST | PDUFlags.MORE_SEGMENTS)
            )

            if segmented:
                invoke_id = apdu[1]
                sequence_number = apdu[2]
                window_size = apdu[3]
                service_choice = apdu[4]
                data_parts = [apdu[5:]]
                more_segments = bool(apdu[0] & PDUFlags.MORE_SEGMENTS)

                transport.sendto(_segment_ack(invoke_id, sequence_number, window_size))

                while more_segments:
                    segment = await protocol.receive(timeout=1.0)
                    apdu = segment[apdu_start_index:]
                    apdu_type = apdu[0] >> 4

                    if apdu_type != APDUType.COMPLEX_ACK:
                        raise DecodingError(f"unsupported response type: {apdu_type}")

                    if apdu[1] != invoke_id:
                        raise DecodingError(f"unexpected invoke ID: {apdu[1]}")

                    sequence_number = apdu[2]
                    window_size = apdu[3]
                    data_parts.append(apdu[4:])
                    more_segments = bool(apdu[0] & PDUFlags.MORE_SEGMENTS)

                    transport.sendto(
                        _segment_ack(invoke_id, sequence_number, window_size)
                    )

                full_apdu = bytes(
                    [
                        APDUType.COMPLEX_ACK << 4,
                        invoke_id,
                        service_choice,
                    ]
                ) + b"".join(data_parts)

                bvlc = pack(
                    "!BBH",
                    BVLC_TYPE,
                    BVLC_FUNCTION_UNICAST,
                    BVLC_LENGTH + len(NPDU) + len(full_apdu),
                )
                response = bvlc + NPDU + full_apdu

            try:
                return _parse_read_property_multiple_response(response)
            except DecodingError as exc:
                raise DecodingError(
                    f"response decoding failed: {exc}\n{response.hex()}"
                ) from exc
        finally:
            transport.close()

    async def write(self, device_property: DeviceProperty, value: Any):
        request = _write_property(device_property, value)

        response = await self._send(request)

        try:
            return _parse_write_property_response(response)
        except DecodingError as exc:
            raise DecodingError(
                f"response decoding failed: {exc}\n{response.hex()}"
            ) from exc
