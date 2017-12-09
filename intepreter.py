import re
pattern = re.compile('(\$\w+\$)')


class AZMError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def value(string, memory={}):
    string = str(string)
    if len(string) == 0:
        return None
    if string[0] == '$':
        if string[1:] in memory:
            return value(memory[string[1:]], memory)
        else:
            raise AZMError('Memory does not have a value `%s`' % string[1:])
    if string[0] == "'" and string[-1] == "'":
        return string[1:1]
    if string[0] == '"' and string[-1] == '"':
        return string[1:1]
    try:
        return int(string)
    except:
        pass
    if string.lower() == 'true':
        return True
    return string


def mainloop(program):
    cursor = 0
    memory = {}
    label = {}

    def require(param, count, command):
        if len(param) != count:
            raise AZMError('Command %s requires %i arguments!' %
                           (command, count))

    def _set(param):
        require(param, 2, 'set')
        if param[0][0] != '$':
            raise AZMError('Variable name must starts with $')
        memory[param[0][1:]] = value(param[1], memory)

    def add(param):
        require(param, 2, 'add')
        if param[0][0] != '$':
            raise AZMError('Variable name must starts with $')
        memory[param[0][1:]] += value(param[1], memory)

    def sub(param):
        require(param, 2, 'sub')
        if param[0][0] != '$':
            raise AZMError('Variable name must starts with $')
        memory[param[0][1:]] -= value(param[1], memory)

    def mul(param):
        require(param, 2, 'mul')
        if param[0][0] != '$':
            raise AZMError('Variable name must starts with $')
        memory[param[0][1:]] *= value(param[1], memory)

    def div(param):
        require(param, 2, 'div')
        if param[0][0] != '$':
            raise AZMError('Variable name must starts with $')
        memory[param[0][1:]] /= value(param[1], memory)

    def xor(param):
        require(param, 2, 'xor')
        if param[0][0] != '$':
            raise AZMError('Variable name must starts with $')
        memory[param[0][1:]] ^= value(param[1], memory)

    def _or(param):
        require(param, 2, 'or')
        if param[0][0] != '$':
            raise AZMError('Variable name must starts with $')
        memory[param[0][1:]] |= value(param[1], memory)

    def _and(param):
        require(param, 2, 'and')
        if param[0][0] != '$':
            raise AZMError('Variable name must starts with $')
        memory[param[0][1:]] &= value(param[1], memory)

    def _not(param):
        require(param, 1, 'not')
        memory[param[0]] = not memory[param[0]]

    def jmp(param):
        require(param, 1, 'jmp')
        tempCursor = value(param[0], memory)
        nonlocal cursor
        cursor = (type(tempCursor)
                  is int and tempCursor or label[tempCursor]) - 1

    def jmpless(param):
        require(param, 3, 'jmp<')
        if value(param[0], memory) < value(param[1], memory):
            tempCursor = value(param[2], memory)
            nonlocal cursor
            cursor = (type(
                tempCursor) is int and tempCursor or label[tempCursor]) - 1

    def jmpgreater(param):
        require(param, 3, 'jmp>')
        if value(param[0], memory) > value(param[1], memory):
            tempCursor = value(param[2], memory)
            nonlocal cursor
            cursor = (type(
                tempCursor) is int and tempCursor or label[tempCursor]) - 1

    def jmpequal(param):
        require(param, 3, 'jmp=')
        if value(param[0], memory) == value(param[1], memory):
            tempCursor = value(param[2], memory)
            nonlocal cursor
            cursor = (type(
                tempCursor) is int and tempCursor or label[tempCursor]) - 1

    def jmpneq(param):
        require(param, 3, 'jmp!')
        if value(param[0], memory) != value(param[1], memory):
            tempCursor = value(param[2], memory)
            nonlocal cursor
            cursor = (type(
                tempCursor) is int and tempCursor or label[tempCursor]) - 1

    def _print(param):
        join = ' '.join(param)
        for replaceable in pattern.findall(join):
            join = join.replace(replaceable, str(
                value(replaceable[0:-1], memory)))
        print(join)

    def _label(param):
        require(param, 1, 'label')
        label[param[0]] = cursor

    def _exit(param):
        require(param, 1, 'exit')
        print('Program exits with code ' + param[0])
        exit()
    commands = {'set': _set, 'add': add, 'sub': sub, 'mul': mul, 'div': div, 'xor': xor, 'or': _or, 'and': _and, 'not': _not,
                'jmp': jmp, 'jmp<': jmpless, 'jmp>': jmpgreater, 'jmp=': jmpequal, 'jmp!': jmpneq,
                'print': _print, 'label': _label, 'exit': _exit}
    lines = program.split('\n')
    while len(lines) > cursor:
        words = lines[cursor].split()
        cursor += 1
        if len(words) < 1:
            continue
        if words[0] in commands:
            try:
                commands[words[0]](words[1:])
            except AZMError as e:
                print(e)
                print('at line %s' % cursor)
        else:
            print('undefined command %s found at line %i' % (words[0], cursor))


if __name__ == '__main__':
    import sys
    mainloop(open(sys.argv[1], 'r').read())
