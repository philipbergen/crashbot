import simcpu
from collections import namedtuple

TICKS_PER_TIMEUNIT = 128
TOP_SPEED = 3
SCANNER_RANGE = 2
SCANNER_GRID = (SCANNER_RANGE*2+1) ** 2
MemoryMap = namedtuple('MemoryMap', ['map', 'armor', 'heading', 'speed', 'steer'])
MEMORY_MAP = MemoryMap(*[simcpu.MEMSIZE - SCANNER_GRID - p for p in range(5)])

class Properties(object):
    def __init__(self, **kwargs):
        for key, val in kwargs.iteritems():
            setattr(self, key, val)

COMPASS = 'NESW0'
class Robot(object):
    '''
    Cpu controlled robot.
    '''
    def __init__(self, cpu):
        self.cpu = cpu
        self.health = 100
        self.pos = Properties(x=0, y=0)
        self.heading = '0'
        self.speed = 0

    def steer(self):
        pass
