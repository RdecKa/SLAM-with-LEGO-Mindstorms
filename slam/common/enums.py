import enum


class GraphType(enum.Enum):
    SCATTER = enum.auto()
    HEATMAP = enum.auto()


class Existence(enum.Enum):
    PERMANENT = enum.auto()
    TEMPORARY = enum.auto()


class Message(enum.Enum):
    DELETE_TEMPORARY_DATA = enum.auto()


class PathId(enum.Enum):
    ROBOT_HISTORY = enum.auto()
    ROBOT_PATH_PLAN = enum.auto()
