import enum


class GraphType(enum.Enum):
    SCATTER = enum.auto()
    HEATMAP = enum.auto()


class Existence(enum.Enum):
    PERMANENT = enum.auto()
    TEMPORARY = enum.auto()


class Message(enum.Enum):
    DELETE_TEMPORARY_DATA = enum.auto()
