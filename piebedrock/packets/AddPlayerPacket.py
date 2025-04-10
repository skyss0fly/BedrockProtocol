from typing import List, Optional
from uuid import UUID

class AddPlayerPacket(DataPacket): 
    NETWORK_ID = ProtocolInfo.ADD_PLAYER_PACKET  # todo: define protocol info 

    def __init__(self):
        super().__init__()
        self.uuid: UUID
        self.username: str
        self.actor_runtime_id: int
        self.platform_chat_id: str = ""
        self.position: Vector3
        self.motion: Optional[Vector3] = None
        self.pitch: float = 0.0
        self.yaw: float = 0.0
        self.head_yaw: float = 0.0
        self.item: ItemStackWrapper
        self.game_mode: int
        self.metadata: List[MetadataProperty] = []
        self.synced_properties: PropertySyncData
        self.abilities_packet: UpdateAbilitiesPacket
        self.links: List[EntityLink] = []
        self.device_id: str = ""
        self.build_platform: int = DeviceOS.UNKNOWN

    @staticmethod
    def create(
        uuid: UUID,
        username: str,
        actor_runtime_id: int,
        platform_chat_id: str,
        position: Vector3,
        motion: Optional[Vector3],
        pitch: float,
        yaw: float,
        head_yaw: float,
        item: ItemStackWrapper,
        game_mode: int,
        metadata: List[MetadataProperty],
        synced_properties: PropertySyncData,
        abilities_packet: 'UpdateAbilitiesPacket',
        links: List[EntityLink],
        device_id: str,
        build_platform: int
    ) -> 'AddPlayerPacket':
        result = AddPlayerPacket()
        result.uuid = uuid
        result.username = username
        result.actor_runtime_id = actor_runtime_id
        result.platform_chat_id = platform_chat_id
        result.position = position
        result.motion = motion
        result.pitch = pitch
        result.yaw = yaw
        result.head_yaw = head_yaw
        result.item = item
        result.game_mode = game_mode
        result.metadata = metadata
        result.synced_properties = synced_properties
        result.abilities_packet = abilities_packet
        result.links = links
        result.device_id = device_id
        result.build_platform = build_platform
        return result

    def decode_payload(self, inp: PacketSerializer) -> None:
        self.uuid = inp.get_uuid()
        self.username = inp.get_string()
        self.actor_runtime_id = inp.get_actor_runtime_id()
        self.platform_chat_id = inp.get_string()
        self.position = inp.get_vector3()
        self.motion = inp.get_vector3()
        self.pitch = inp.get_lfloat()
        self.yaw = inp.get_lfloat()
        self.head_yaw = inp.get_lfloat()
        self.item = inp.get_item_stack_wrapper()
        self.game_mode = inp.get_varint()
        self.metadata = inp.get_entity_metadata()
        self.synced_properties = PropertySyncData.read(inp)

        self.abilities_packet = UpdateAbilitiesPacket()
        self.abilities_packet.decode_payload(inp)

        link_count = inp.get_unsigned_varint()
        self.links = [inp.get_entity_link() for _ in range(link_count)]

        self.device_id = inp.get_string()
        self.build_platform = inp.get_lint()

    def encode_payload(self, out: PacketSerializer) -> None:
        out.put_uuid(self.uuid)
        out.put_string(self.username)
        out.put_actor_runtime_id(self.actor_runtime_id)
        out.put_string(self.platform_chat_id)
        out.put_vector3(self.position)
        out.put_vector3_nullable(self.motion)
        out.put_lfloat(self.pitch)
        out.put_lfloat(self.yaw)
        out.put_lfloat(self.head_yaw)
        out.put_item_stack_wrapper(self.item)
        out.put_varint(self.game_mode)
        out.put_entity_metadata(self.metadata)
        self.synced_properties.write(out)

        self.abilities_packet.encode_payload(out)

        out.put_unsigned_varint(len(self.links))
        for link in self.links:
            out.put_entity_link(link)

        out.put_string(self.device_id)
        out.put_lint(self.build_platform)

    def handle(self, handler: 'PacketHandlerInterface') -> bool:
        return handler.handle_add_player(self)
