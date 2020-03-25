import random
import time

import slam.display.map as smap

if __name__ == "__main__":
    map = smap.Map(10, 10)
    for _ in range(10):
        map.add_data(random.randint(0, 10), random.randint(0, 10))
        map.redraw()
        time.sleep(1)
