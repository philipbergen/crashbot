# -*- coding: utf-8 -*-

import simcpu
from itertools import chain

TOP_SPEED = 10
SCANNER_RANGE = 3
SCANNER_GRID = (SCANNER_RANGE*2+1) ** 2

class Properties(object):
    def __init__(self, **kwargs):
        for key, val in kwargs.iteritems():
            setattr(self, key, val)

class Robot(object):
    '''
    Cpu controlled robot.
    '''

    base_program = ("""
    @0
    jump _pgmstart
    _speed:
    =0
    _heading:
    =0
    _desired_speed:
    =0
    _desired_heading:
    =0
    _health:
    =100
    _pos_x:
    =0
    _pos_y:
    =0
    _scanner:
    """ + '\n'.join(['=0' for _ in range(SCANNER_GRID)]) + """
    _pgmstart:
    """).split('\n')

    def __init__(self, name, pos_x, pos_y, scanner, program):
        '''
        Creates a robot.
        name -- Any string, not too long though
        pos_x -- Initial horizontal position
        pos_y -- Initial vertical position
        scanner -- callback method that returns a grid around a point, takes two args: x, y
        program -- Line iterator for robot control program
        '''
        self.name = name
        self.health = 100
        self.pos_x = pos_x * 10
        self.pos_y = pos_y * 10
        self.speed = 0
        self.heading = 0
        self.desired_speed = 0
        self.desired_heading = 0
        self.scanner = scanner
        self.cpu = simcpu.Cpu(name)
        self.cpu.load(chain(Robot.base_program, program))

    def cpu_cycles(self, cycles):
        for a in xrange(cycles):
            self.cpu.cpu_cycle()

    def pre_move(self):
        self.desired_speed = self.cpu.get_value('@_desired_speed')
        self.desired_heading = self.cpu.get_value('@_desired_heading')
        
    def move(self):
        self.speed = max(0, min(TOP_SPEED, int(self.desired_speed)))
        self.heading = ((self.desired_heading % 360) // 90) * 90
        if self.heading == 0:
            print "HEADING 0:", self.pos_y, self.speed
            self.pos_y -= self.speed
        elif self.heading == 180:
            print "HEADING 180:", self.pos_y, self.speed
            self.pos_y += self.speed
        elif self.heading == 90:
            print "HEADING 90:", self.pos_x, self.speed
            self.pos_x += self.speed
        elif self.heading == 270:
            print "HEADING 270:", self.pos_x, self.speed
            self.pos_x -= self.speed
        else:
            raise RuntimeException("Unsupported heading: " + str(self.heading))

    def post_move(self):
        def set_ro(label, val):
            addr = self.cpu.get_address(label)
            self.cpu.memory[addr] = simcpu.Getable(val)
        set_ro('_speed', self.speed)
        set_ro('_heading', self.heading)
        set_ro('_health', self.health)
        set_ro('_pos_x', self.pos_x // 10)
        set_ro('_pos_y', self.pos_y // 10)
        scanbase = self.cpu.get_address('_scanner')
        for idx, val in enumerate(self.scanner(self.pos_x // 10, self.pos_y // 10)):
            self.cpu.memory[scanbase + idx] = val

    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        return '<Robot(%r, %r, %r, <scanner>, <program>) health=%r, speed=%r, heading=%r, desired_speed=%r, desired_heading=%r>' % (self.name, self.pos_x // 10, self.pos_y // 10, self.health, self.speed, self.heading, self.desired_speed, self.desired_heading)

def empty_scanner(x,y):
    return [0 for r in range(SCANNER_GRID)]

if __name__ == '__main__':
    rob = Robot('test', 10, 10, empty_scanner, '''
    trace
copy @_desired_speed 1
copy R0 0
loop:
copy @_desired_heading R0
compute R0 + R0 1
test R0 < 360
jumpif loop
halt
    '''.split('\n'))
    while not rob.cpu.halted_flag:
        print "STILL NOT HALTED"
        rob.cpu_cycles(30)
        rob.pre_move()
        rob.move()
        rob.post_move()
    print rob
    print rob.cpu
