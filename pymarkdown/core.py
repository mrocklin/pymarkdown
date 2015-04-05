from itertools import chain


def istriplebacktick(line):
    return line.startswith('```')

def partition_by_blocks(lines, isstart=istriplebacktick, isend=istriplebacktick):
    part = list()
    in_code_block = False
    for line in lines:
        if not in_code_block and isstart(line):
            yield {'type': 'prose', 'content': part}
            part = [line]
            in_code_block = True
        elif in_code_block and isend(line):
            part.append(line)
            yield {'type': 'code', 'content': part}
            part = []
            in_code_block = False
        else:
            part.append(line)

    if in_code_block:
        yield {'type': 'code', 'content': part}
    else:
        yield {'type': 'prose', 'content': part}


def transform_prose(lines):
    """

    >>> transform_prose(['Title', '-----'])
    ['Title', '-----']
    """
    return lines

def transform_code(lines, scope=dict()):
    """

    >>> text = [">>> 1 + 1"]
    >>> transform_code(text)
    ['>>> 1 + 1', '2']
    """
    out = list()
    seq = iter(lines)
    try:
        while True:
            line = next(seq)
            out.append(line)
            if line.lstrip().startswith('>>>'):
                result = repr(eval(line.lstrip(' >'), scope))
                out.extend(result.split('\n'))
                seq = burn_results(seq)
    except StopIteration:
        pass
    return out


def burn_results(seq):
    item = next(seq).lstrip()
    while item and not (item.startswith('>>>') or item.startswith('```')):
        item = next(seq).lstrip()
    return chain([item], seq)

transformers = {'code': transform_code, 'prose': transform_prose}

def transform(part):
    """ Transform one part/block of the text """
    rv = part.copy()
    rv['content'] = transformers[part['type']](part['content'])
    return rv


def render(text):
    """ Render pymarkdown text """
    lines = text.split('\n')
    parts = partition_by_blocks(lines)
    parts2 = map(transform, parts)

    lines = [line for part in parts2 for line in part['content']]

    return '\n'.join(lines)
