CRASHBOTS
========

The simulated CPU has a small number of instructions, see simcpu.py.

Use the CPU like this:

    >>> from simcpu import Cpu
    >>> cpu = Cpu('Test 1')
    >>> program='''# Program starts at address zero always
    ... # Jump over variables
    ... @0
    ...  jump main
    ... # Declare variables
    ...  hello:
    ... ='Hello, world!'
    ...  main:
    ...     debug @hello
    ...     halt
    ... '''
    >>> cpu.load(program.split('\n'))
    >>> cpu.run()
    ----==| DEBUG |==----
    NAME: Test 1 TEST: False PC: 2 REGISTERS: [None, None, None, None] STACK: [] INSTRUCTION:
    main:
        debug @hello
    DEBUG: Hello, world!
