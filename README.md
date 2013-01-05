crashbot
========

Programming tutorial/game for Olfert and Wilton Friberg.

Author -- Philip Bergen

To build/test the python code:

    py/build.sh

To run a game:

    py/run.sh <robot 1 program> <robot 2 program>

For more info about the program go look at the `py` directory.

Idea
====

Simulated CPUs run little robots around an arena. Robots cause damage
by crashing into other robots. Crashing into walls causes damage to
robots. Try to crash another robot into a wall!

Crashing robots swap speed and heading with each other. Crashing into
a wall reduces the speed to zero.

Each robot has two simple controls:
* Speed
* Heading

Each robot also has a scanner that keeps a map of the immediate
surroundings. Robots the scanner spots will also reveal their speed
and heading.

Rules
====

Damage
-------

Damage is dealt based on the attacker's speed. 

Hits from the side deal damage equal to the speed of the
attacker. Hits from behind deal damage equal to how much faster than
the target the attacker is moving. Only if robots collide head on do
they both get damage.

Crashing into walls causes damage to equal to the robot's speed.

Crashing robots swap speed and heading with each other. Crashing into
a wall reduces the speed to zero.

Time
----
Time is counted in ticks. Each tick awards the robots a limited number
of CPU cycles.

Movement
---------

Heading and speed. Heading is degrees, zero is north (or up), 90 is
east (or right).

Speed is a digit from 0 to 10. At speed 10 the robot moves one square
each tick. The robot moves according to controls at the end each tick.

Scanner
-------

Scans the surrounding 7x7 squares updated. The scanner output is a
vector with contents `0`: nothing, `1-9`: robot number, `'W'`: wall

Your own robot ID will always be in the center.

Example:

    000000W
    000000W
    000300W
    001002W
    000000W

Note that `'W'` is a string and the empty + robot ID are integers.


Programming
------------

System/reserved labels begin with underscore (`_`), please avoid using
underscore in your labels.

### Scanner

The scanner squares are located at `_scanner`. An easy way to analyze
the vector is using `R2` and `R3`:

    compute R2 * 7 7
    copy _scanner R3
    look:
	test @R3 = 'W'
	callif avoid_wall
	test @R3 > '0'
	callif attack_robot
	compute R2 - R2 1
	test R2 >= 0
	jumpif look

To query the scanner put the robot ID in `R0` and call `_position`:

    copy 1 R0
    call _position
    copy R0 speed
    copy R1 heading

