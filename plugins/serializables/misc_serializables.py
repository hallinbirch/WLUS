from pyraknet import bitstream
import random
from plugins.easy_cdclient.cdclient_objects import GameObject
from plugins.easy_cdclient.cdclient_tables import MinifigComponentTable
from xml.etree import ElementTree


class LUZScene(bitstream.Serializable):
    def __init__(self):
        self.filename = ""
        self.id = 0
        self.name = ""

    def serialize(self, stream: bitstream.WriteStream) -> None:
        raise Exception("This struct cannot be serialized")

    @classmethod
    def deserialize(cls, stream: bitstream.ReadStream) -> bitstream.Serializable:
        luz_scene = LUZScene()
        luz_scene.filename = CString(length_type=bitstream.c_uint8).deserialize(stream)
        luz_scene.id = stream.read(bitstream.c_uint8)
        stream.read(bytes, length=3)
        stream.read(bitstream.c_uint8)
        stream.read(bytes, length=3)
        luz_scene.name = CString(length_type=bitstream.c_uint8).deserialize(stream)
        stream.read(bytes, length=3)
        return luz_scene


class LUZ(bitstream.Serializable):
    def __init__(self):
        self.version = 0
        self.world_id = 0
        self.spawnpoint_position = Vector3()
        self.spawnpoint_rotation = Vector4()
        self.scenes = []

    def serialize(self, stream: bitstream.WriteStream) -> None:
        raise Exception("This struct cannot be serialized")

    @classmethod
    def deserialize(cls, stream: bitstream.ReadStream) -> bitstream.Serializable:
        luz = LUZ()
        luz.version = stream.read(bitstream.c_ulong)
        if luz.version >= 0x24:
            stream.read(bitstream.c_ulong)
        luz.world_id = stream.read(bitstream.c_ulong)
        if luz.version >= 0x26:
            luz.spawnpoint_position = stream.read(Vector3)
            luz.spawnpoint_rotation = stream.read(Vector4)
        if luz.version < 0x25:
            scene_count = stream.read(bitstream.c_uint8)
        else:
            scene_count = stream.read(bitstream.c_ulong)
        for _ in range(scene_count):
            luz.scenes.append(stream.read(LUZScene))
        return luz


class CString(bitstream.Serializable):
    def __init__(self, data='', allocated_length=None, length_type=None):
        self.data = data
        self.allocated_length = allocated_length
        self.length_type = length_type

    def serialize(self, stream: bitstream.WriteStream) -> None:
        stream.write(self.data if isinstance(self.data, bytes) else bytes(self.data, 'latin1'),
                     allocated_length=self.allocated_length, length_type=self.length_type)

    def deserialize(self, stream: bitstream.ReadStream):
        return stream.read(bytes, allocated_length=self.allocated_length, length_type=self.length_type).decode('latin1')


class Vector3(bitstream.Serializable):
    def __init__(self):
        self.x: float = 0.0
        self.y: float = 0.0
        self.z: float = 0.0

    def __add__(self, other):
        result = Vector3()
        result.x = self.x + other.x
        result.y = self.y + other.y
        result.z = self.z + other.z
        return result

    def __sub__(self, other):
        result = Vector3()
        result.x = self.x - other.x
        result.y = self.y - other.y
        result.z = self.z - other.z
        return result

    def __str__(self):
        return str(self.x) + "," + str(self.y) + "," + str(self.z)

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y and self.z == other.z:
            return True
        else:
            return False

    @classmethod
    def deserialize(cls, stream: bitstream.ReadStream) -> bitstream.Serializable:
        result = Vector3()
        result.x = stream.read(bitstream.c_float)
        result.y = stream.read(bitstream.c_float)
        result.z = stream.read(bitstream.c_float)
        return result

    def serialize(self, stream: bitstream.WriteStream) -> None:
        stream.write(bitstream.c_float(self.x))
        stream.write(bitstream.c_float(self.y))
        stream.write(bitstream.c_float(self.z))


class Vector4(bitstream.Serializable):
    def __init__(self):
        self.x: float = 0.0
        self.y: float = 0.0
        self.z: float = 0.0
        self.w: float = 0.0

    def __add__(self, other):
        result = Vector3()
        result.x = self.x + other.x
        result.y = self.y + other.y
        result.z = self.z + other.z
        result.w = self.w + other.w
        return result

    def __sub__(self, other):
        result = Vector3()
        result.x = self.x - other.x
        result.y = self.y - other.y
        result.z = self.z - other.z
        result.w = self.w - other.w
        return result

    def __str__(self):
        return str(self.x) + "," + str(self.y) + "," + str(self.z) + "," + str(self.w)

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y and self.z == other.z and self.w == other.w:
            return True
        else:
            return False

    @classmethod
    def deserialize(cls, stream: bitstream.ReadStream) -> bitstream.Serializable:
        result = Vector3()
        result.x = stream.read(bitstream.c_float)
        result.y = stream.read(bitstream.c_float)
        result.z = stream.read(bitstream.c_float)
        result.w = stream.read(bitstream.c_float)
        return result

    def serialize(self, stream: bitstream.WriteStream) -> None:
        stream.write(bitstream.c_float(self.x))
        stream.write(bitstream.c_float(self.y))
        stream.write(bitstream.c_float(self.z))
        stream.write(bitstream.c_float(self.w))


class LwoObjID:
    """
    This is the data type that object ids are made out of.
    They are different from normal 64 bit ints because they have flags that must be set.
    """
    @classmethod
    def gen_lwoobjid(cls, persistent: bool = False, client: bool = False, spawned: bool = False,
                     character: bool = False):
        number = random.randrange(0, (2**32) - 1)
        number = number | (int(persistent) << 32)
        number = number | (int(client) << 46)
        number = number | (int(spawned) << 58)
        number = number | (int(character) << 60)
        return number


class LDF(bitstream.Serializable):
    """
    Lego Data Format
    """
    def __init__(self):
        self._keys: list = []

    def register_key(self, key_name: str, value: any, value_type: int):
        self._keys.append([key_name, value, value_type])

    def serialize(self, stream: bitstream.WriteStream) -> None:
        key_num = len(self._keys)
        stream.write(bitstream.c_uint(key_num))
        for key in self._keys:
            name = key[0]
            value = key[1]
            value_type = key[2]
            stream.write(bitstream.c_uint8(len(name) * 2))
            for char in name:
                stream.write(char.encode('latin1'))
                stream.write(b'\0')
            stream.write(bitstream.c_ubyte(value_type))
            if value_type == 0:
                stream.write(value, length_type=bitstream.c_uint)
            elif value_type == 1:
                stream.write(bitstream.c_int(value))
            elif value_type == 3:
                stream.write(bitstream.c_float(value))
            elif value_type == 5:
                stream.write(bitstream.c_uint(value))
            elif value_type == 7:
                stream.write(bitstream.c_bool(value))
            elif value_type == 8 or value_type == 9:
                stream.write(bitstream.c_int64(value))
            elif value_type == 13:
                xml_str = bytes(ElementTree.tostring(value))
                xml_str = b'<?xml version="1.0">' + xml_str
                stream.write(bitstream.c_ulong(xml_str.__len__()))
                stream.write(xml_str)

    @classmethod
    def deserialize(cls, stream: bitstream.ReadStream) -> bitstream.Serializable:
        raise Exception("This struct cannot be deserialized")


class LoginCharacter(bitstream.Serializable):
    """
    This is a serializable that creates the struct which is repeated in the minfigure list packet
    """
    def __init__(self):
        self.object_id = 1124
        self.current_name = ""
        self.unapproved_name = ""
        self.name_rejected = False
        self.is_ftp = False
        self.head_color = 0
        self.head = 0
        self.chest_color = 0
        self.chest = 0
        self.legs = 0
        self.hair_style = 0
        self.hair_color = 0
        self.left_hand = 0
        self.right_hand = 0
        self.eyebrows_style = 0
        self.eyes_style = 0
        self.mouth_style = 0
        self.last_zone = 0
        self.last_map_instance = 0
        self.last_map_clone = 0
        self.equipped_items = []

    @classmethod
    def deserialize(cls, stream: bitstream.ReadStream) -> bitstream.Serializable:
        raise Exception("This struct cannot be deserialized")

    def serialize(self, stream: bitstream.WriteStream) -> None:
        stream.write(bitstream.c_uint64(self.object_id))
        stream.write(bitstream.c_uint32(0))
        stream.write(self.current_name, allocated_length=33)
        stream.write(self.unapproved_name, allocated_length=33)
        stream.write(bitstream.c_bool(self.name_rejected))
        stream.write(bitstream.c_bool(self.is_ftp))
        stream.write(bitstream.c_uint32(self.head_color))
        stream.write(bitstream.c_uint16(0))
        stream.write(bitstream.c_uint32(self.head))
        stream.write(bitstream.c_uint32(self.chest_color))
        stream.write(bitstream.c_uint32(self.chest))
        stream.write(bitstream.c_uint32(self.legs))
        stream.write(bitstream.c_uint32(self.hair_style))
        stream.write(bitstream.c_uint32(self.hair_color))
        stream.write(bitstream.c_uint32(self.left_hand))
        stream.write(bitstream.c_uint32(self.right_hand))
        stream.write(bitstream.c_uint32(self.eyebrows_style))
        stream.write(bitstream.c_uint32(self.eyes_style))
        stream.write(bitstream.c_uint32(self.mouth_style))
        stream.write(bitstream.c_uint32(0))
        stream.write(bitstream.c_uint16(self.last_zone))
        stream.write(bitstream.c_uint16(self.last_map_instance))
        stream.write(bitstream.c_uint32(self.last_map_clone))
        stream.write(bitstream.c_uint64(0))
        stream.write(bitstream.c_uint16(len(self.equipped_items)))
        for item in self.equipped_items:
            stream.write(bitstream.c_uint32(item))

    # For testing just use lot 6010
    @classmethod
    def from_cdclient(cls, lot: int):
        char = LoginCharacter()
        minifig_object = GameObject(lot)
        char.current_name = str(minifig_object.object_data.displayName).split("-")[0]
        if 17 in minifig_object.components:
            equipped = []
            for item in minifig_object.components[17]:
                if item.equip == 1:
                    equipped.append(item.itemid)
            char.equipped_items = equipped
        if 35 in minifig_object.components:
            minifig_comp: MinifigComponentTable = minifig_object.components[35]
            char.head = minifig_comp.head
            char.chest_color = minifig_comp.chestdecal
            char.legs = minifig_comp.legs
            char.hair_style = minifig_comp.hairstyle
            char.hair_color = minifig_comp.haircolor
            char.chest = minifig_comp.chest
            char.head_color = minifig_comp.headcolor
            char.left_hand = minifig_comp.lefthand
            char.right_hand = minifig_comp.righthand
            char.eyebrows_style = minifig_comp.eyebrowstyle
            char.eyes_style = minifig_comp.eyesstyle
            char.mouth_style = minifig_comp.mouthstyle
        char.object_id = LwoObjID.gen_lwoobjid(persistent=True, character=True)
        return char

    def save_to_db(self, account_id, connection):
        c = connection.cursor()
        c.execute("INSERT INTO wlus.character (character_id, current_name, requested_name, head_color,"
                  " head, chest_color, chest, legs, hair_style, hair_color, left_hand, right_hand,"
                  " eyebrow_style, eye_style, mouth_style, account_id, zone) VALUES (%s, %s, %s, %s, %s, %s, %s, "
                  "%s, %s, %s, %s, %s, %s, %s, %s, %s, 0)",
                  (self.object_id, self.current_name, self.unapproved_name,self.head_color, self.head, self.chest_color,
                   self.chest, self.legs, self.hair_style, self.hair_color, self.left_hand, self.right_hand,
                   self.eyebrows_style, self.eyes_style, self.mouth_style, account_id))
        c.execute('INSERT INTO `wlus`.`character_info` (`player_id`,`position`,`rotation`,`health`,`max_health`,'
                  '`armor`,`max_armor`,`imagination`,`max_imagination`,`backpack_space`,`currency`,`universe_score`'
                  ',`level`) VALUES (%s,"0,0,0","0,0,0,0",4,4,0,0,0,0,20,0,0,0);', (self.object_id,))
        c.execute('INSERT INTO `wlus`.`character_stats`(`currency_collected`,`bricks_collected`,'
                  '`smashables_smashed`,`quick_builds_done`,`enemies_smashed`,`rockets_used`,`pets_tamed`,'
                  '`imagination_collected`,`health_collected`,`armor_collected`,`distance_traveled`,`times_died`,'
                  '`damage_taken`,`damage_healed`,`armor_repaired`,`imagination_restored`,`imagination_used`,'
                  '`distance_driven`,`time_airborne_in_car`,`racing_imagination_collected`,'
                  '`racing_imagination_crates_smashed`,`race_car_boosts`,`car_wrecks`,`racing_smashables_smashed`,'
                  '`races_finished`,`races_won`,`player_id`) VALUES '
                  '(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,%s);', (self.object_id,))

        for i in range(len(self.equipped_items)):
            item_id = LwoObjID.gen_lwoobjid()
            c.execute("INSERT INTO wlus.inventory (object_id, lot, slot, equipped, linked, quantity, player_id)"
                      "VALUES (%s, %s, %s, 1, 1, 1, %s)", (item_id, self.equipped_items[i], i, self.object_id))
        connection.commit()


