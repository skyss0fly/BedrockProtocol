from abc import ABC, abstractmethod

class PacketDecodeException(Exception):
    @staticmethod
    def wrap(exception, packet_name):
        return PacketDecodeException(f"{packet_name}: {str(exception)}")

class BinaryDataException(Exception):
    pass

class PacketSerializer:
    # Placeholder methods
    def get_unsigned_varint(self):
        pass

    def put_unsigned_varint(self, value):
        pass

class Packet(ABC):
    @abstractmethod
    def pid(self) -> int:
        pass

    @abstractmethod
    def encode(self, out: PacketSerializer) -> None:
        pass

    @abstractmethod
    def decode(self, inp: PacketSerializer) -> None:
        pass

class DataPacket(Packet):
    NETWORK_ID = 0

    PID_MASK = 0x3FF  # 10 bits
    SUBCLIENT_ID_MASK = 0x03  # 2 bits
    SENDER_SUBCLIENT_ID_SHIFT = 10
    RECIPIENT_SUBCLIENT_ID_SHIFT = 12

    def __init__(self):
        self.sender_sub_id = 0
        self.recipient_sub_id = 0

    def pid(self) -> int:
        return self.NETWORK_ID

    def get_name(self) -> str:
        return self.__class__.__name__

    def can_be_sent_before_login(self) -> bool:
        return False

    def decode(self, inp: PacketSerializer) -> None:
        try:
            self.decode_header(inp)
            self.decode_payload(inp)
        except (BinaryDataException, PacketDecodeException) as e:
            raise PacketDecodeException.wrap(e, self.get_name())

    def decode_header(self, inp: PacketSerializer) -> None:
        header = inp.get_unsigned_varint()
        pid = header & self.PID_MASK
        if pid != self.NETWORK_ID:
            raise PacketDecodeException(f"Expected {self.NETWORK_ID} for packet ID, got {pid}")
        self.sender_sub_id = (header >> self.SENDER_SUBCLIENT_ID_SHIFT) & self.SUBCLIENT_ID_MASK
        self.recipient_sub_id = (header >> self.RECIPIENT_SUBCLIENT_ID_SHIFT) & self.SUBCLIENT_ID_MASK

    @abstractmethod
    def decode_payload(self, inp: PacketSerializer) -> None:
        pass

    def encode(self, out: PacketSerializer) -> None:
        self.encode_header(out)
        self.encode_payload(out)

    def encode_header(self, out: PacketSerializer) -> None:
        out.put_unsigned_varint(
            self.NETWORK_ID |
            (self.sender_sub_id << self.SENDER_SUBCLIENT_ID_SHIFT) |
            (self.recipient_sub_id << self.RECIPIENT_SUBCLIENT_ID_SHIFT)
        )

    @abstractmethod
    def encode_payload(self, out: PacketSerializer) -> None:
        pass

    def __getattr__(self, name):
        raise AttributeError(f"Undefined property: {self.__class__.__name__}::{name}")

    def __setattr__(self, name, value):
        if name not in {"sender_sub_id", "recipient_sub_id", "NETWORK_ID"} and not name.startswith("_"):
            raise AttributeError(f"Undefined property: {self.__class__.__name__}::{name}")
        super().__setattr__(name, value)
