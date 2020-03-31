from __future__ import annotations

import slam.common.geometry as geometry


class Node():
    def __init__(self, location: geometry.Point, parent: Node = None):
        self.parent = parent
        self.location = location


class Graph():
    def __init__(self):
        self.nodes = []

    def __len__(self):
        return len(self.nodes)

    def __getitem__(self, key):
        if not isinstance(key, int):
            raise TypeError("Wrong key type")
        if key >= 0 and key < len(self.nodes):
            return self.nodes[key]
        raise IndexError(f"Key {key} out of range for array of length "
                         f"{len(self.nodes)}")

    def add_node(self, node: Node):
        self.nodes.append(node)
