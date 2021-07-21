from dataclasses import dataclass
from struct import Struct
from typing import BinaryIO

from relic.sga.shared import ARCHIVE_HEADER_OFFSET
from relic.shared import unpack_from_stream, pack_into_stream


@dataclass
class OffsetInfo:
    __OFFSET_LAYOUT = Struct("< L H")

    offset_relative: int
    count: int

    @property
    def offset_absolute(self) -> int:
        return ARCHIVE_HEADER_OFFSET + self.offset_relative

    @offset_absolute.setter
    def offset_absolute(self, abs_offset: int):
        self.offset_relative = abs_offset - ARCHIVE_HEADER_OFFSET

    @classmethod
    def unpack(cls, stream: BinaryIO) -> 'OffsetInfo':
        return OffsetInfo(*unpack_from_stream(cls.__OFFSET_LAYOUT, stream))

    def pack(self, stream: BinaryIO) -> int:
        args = (self.offset_relative, self.count)
        return pack_into_stream(self.__OFFSET_LAYOUT, stream, *args)