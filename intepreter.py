import re
pattern = re.compile(r'(\$\w+\$)')
operators = {
    '>': lambda x, y: x > y,
    '<': lambda x, y: x < y,
    '>=': lambda x, y: x >= y,
    '<=': lambda x, y: x <= y,
    '==': lambda x, y: x == y,
    '!=': lambda x, y: x != y
}


class AZMError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def replace_variable(string, memory={}):
    result = str(string)
    for replaceable in pattern.findall(result):
        result = result.replace(replaceable, str(
            value(replaceable[0:-1], memory)))
    return result


def value(string, memory={}):
    string = str(string)
    if len(string) == 0:
        return None
    if string[0] == "'" and string[-1] == "'":
        return replace_variable(string[1:1], memory)
    if string[0] == '"' and string[-1] == '"':
        return replace_variable(string[1:1], memory)
    if string[0] == '$':
        if string[1:] in memory:
            return value(memory[string[1:]], memory)
        else:
            raise AZMError('Memory does not have a value `%s`' % string[1:])
    try:
        return float(string)
    except:
        pass
    try:
        return int(string)
    except:
        pass
    if string.lower() == 'true':
        return True
    if string.lower() == 'false':
        return False
    return replace_variable(string, memory)


def mainloop(program):
    cursor = 0
    memory = {}
    label = {}
    if_block = []

    def _require(param, count, command):
        if len(param) != count:
            raise AZMError('Command %s requires %i arguments!' %
                           (command, count))

    def _set(param):
        if len(param) < 2:
            raise AZMError('Command set requires 2 or more arguments!')
        if param[0][0] != '$':
            raise AZMError('Variable name must starts with $')
        memory[param[0][1:]] = value(' '.join(param[1:]), memory)

    def _add(param):
        _require(param, 2, 'add')
        if param[0][0] != '$':
            raise AZMError('Variable name must starts with $')
        memory[param[0][1:]] += value(param[1], memory)

    def _sub(param):
        _require(param, 2, 'sub')
        if param[0][0] != '$':
            raise AZMError('Variable name must starts with $')
        memory[param[0][1:]] -= value(param[1], memory)

    def _mul(param):
        _require(param, 2, 'mul')
        if param[0][0] != '$':
            raise AZMError('Variable name must starts with $')
        memory[param[0][1:]] *= value(param[1], memory)

    def _div(param):
        _require(param, 2, 'div')
        if param[0][0] != '$':
            raise AZMError('Variable name must starts with $')
        memory[param[0][1:]] /= value(param[1], memory)
    def _mod(param):
        _require(param, 2, 'mod')
        if param[0][0] != '$':
            raise AZMError('Variable name must starts with $')
        memory[param[0][1:]] %= value(param[1], memory)

    def _xor(param):
        _require(param, 2, 'xor')
        if param[0][0] != '$':
            raise AZMError('Variable name must starts with $')
        memory[param[0][1:]] ^= value(param[1], memory)

    def _or(param):
        _require(param, 2, 'or')
        if param[0][0] != '$':
            raise AZMError('Variable name must starts with $')
        memory[param[0][1:]] |= value(param[1], memory)

    def _and(param):
        _require(param, 2, 'and')
        if param[0][0] != '$':
            raise AZMError('Variable name must starts with $')
        memory[param[0][1:]] &= value(param[1], memory)

    def _not(param):
        _require(param, 1, 'not')
        memory[param[0]] = not memory[param[0]]

    def _jmp(param):
        _require(param, 1, 'jmp')
        temp_cursor = value(param[0], memory)
        temp_cursor = isinstance(
            temp_cursor, int) and temp_cursor or label[temp_cursor]
        nonlocal cursor
        nonlocal if_block
        if len(if_block) > 0:
            move = cursor - temp_cursor
            if move > 0:
                pop_count = 0
                for line in lines[temp_cursor:cursor]:
                    words = line.strip().split()
                    if len(words) > 0 and words[0] == 'if':
                        pop_count += 1
                if_block = if_block[:len(if_block) - pop_count]
                cursor = temp_cursor
            else:
                if_block[-1] = 'jmp%i' % temp_cursor
        cursor = temp_cursor

    def _jmpc(param):
        _require(param, 4, 'jmpc')
        left, operator, right = (
            value(param[0], memory), param[1], value(param[2], memory))
        if operator in operators:
            if operators[operator](left, right):
                nonlocal cursor
                nonlocal if_block
                temp_cursor = value(param[3], memory)
                temp_cursor = isinstance(
                    temp_cursor, int) and temp_cursor or label[temp_cursor]
                move = cursor - temp_cursor
                if move > 0:
                    pop_count = 0
                    for line in lines[temp_cursor:cursor]:
                        words = line.strip().split()
                        if len(words) > 0 and words[0] == 'if':
                            pop_count += 1
                    if_block = if_block[:len(if_block) - pop_count]
                    cursor = temp_cursor
                else:
                    if_block[-1] = 'jmp%i' % temp_cursor
        else:
            raise AZMError('undefined operator %s found' % operator)

    def _print(param):
        print(replace_variable(' '.join(param), memory))

    def _pass(param):
        pass

    def _exit(param):
        _require(param, 1, 'exit')
        print('Program exits with code ' + param[0])
        exit()

    def _input(param):
        _require(param, 1, 'input')
        if param[0][0] != '$':
            raise AZMError('Variable name must starts with $')
        memory[param[0][1:]] = input()

    def _if(param):
        _require(param, 3, 'if')
        left, operator, right = (
            value(param[0], memory), param[1], value(param[2], memory))
        if operator in operators:
            nonlocal if_block
            if operators[operator](left, right):
                if_block.append('if')
            else:
                if_block.append('to-else')
        else:
            raise AZMError('undefined operator %s found' % operator)

    def _else(param):
        nonlocal if_block
        if len(if_block) > 0:
            if if_block[-1] == 'to-else':
                if_block[-1] = 'else'
            else:
                if_block[-1] = 'to-endif'
        else:
            raise AZMError('if block not found')

    def _elif(param):
        nonlocal if_block
        _require(param, 3, 'elif')
        if len(if_block) > 0:
            if if_block[-1] == 'to-else':
                left, operator, right = (
                    value(param[0], memory), param[1], value(param[2], memory))
                if operators[operator](left, right):
                    if_block[-1] = 'else'
            else:
                if_block[-1] = 'to-endif'
        else:
            raise AZMError('if block not found')

    def _endif(param):
        nonlocal if_block
        if len(if_block) > 0:
            if if_block[-1].startswith('jmp'):
                nonlocal cursor
                cursor = int(if_block[-1][3:])
            if_block.pop()
        else:
            raise AZMError('if block not found')

    commands = {'set': _set, 'add': _add, 'sub': _sub, 'mul': _mul, 'div': _div, 'mod': _mod,
                'xor': _xor, 'or': _or, 'and': _and, 'not': _not,
                'jmp': _jmp, 'jmpc': _jmpc, 'input': _input,
                'if': _if, 'else': _else, 'elif': _elif, 'endif': _endif,
                'print': _print, 'label': _pass, 'rem': _pass, 'exit': _exit}
    lines = program.split('\n')
    cursor = 0
    for line in lines:
        words = line.strip().split()
        if words[0] == 'label':
            if len(words) != 2:
                print('AZM Error: Command label requires 2 arguments!')
                print('  at line %s' % cursor)
                return
            else:
                label[words[1]] = cursor
        cursor += 1
    cursor = 0
    while len(lines) > cursor:
        words = lines[cursor].strip().split()
        cursor += 1
        if len(words) < 1:
            continue
        if len(if_block) > 0:
            if if_block[-1] in ('to-else', 'ignored'):
                if words[0] == 'if':
                    if_block.append('ignored')
                    continue
                elif words[0] not in ('else', 'elif'):
                    continue
            elif if_block[-1] == 'to-endif' and words[0] != 'endif':
                continue
            elif if_block[-1].startswith('jmp') and words[0] != 'endif':
                continue
        if words[0] in commands:
            try:
                commands[words[0]](words[1:])
            except AZMError as e:
                print('AZM Error: %s' % e)
                print('  at line %s' % cursor)
                return
        else:
            print('undefined command %s found at line %i' % (words[0], cursor))


if __name__ == '__main__':
    import sys
    mainloop(open(sys.argv[1], 'r').read())
