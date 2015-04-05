import doctest
import re
from contextlib import contextmanager
from StringIO import StringIO
import itertools
import sys
from toolz.curried import pipe, map, filter, concat


def process(text):
    """ Replace failures in docstring with results """
    parts = pipe(text, parser.parse,
                       filter(None),
                       map(separate_fence),
                       concat, list)

    scope = dict()  # scope of variables in our executed environment
    state = dict()  # state of pymarkdown traversal

    out_parts = list()
    for part in parts:
        out, scope, state = step(part, scope, state)
        out_parts.extend(out)

    head = '\n'.join(sorted(state.get('headers', set())))
    body = pipe(out_parts, map(render_part),
                           filter(None),
                           '\n'.join)
    foot = '\n\n'.join(state.get('footers', []))

    return '\n\n'.join([head, body, foot]).strip()


def step(part, scope, state):
    """ Step through one part of the document

    1.  Prose: pass through
    2.  Code fence: record
    3.  Code: evaluate
    4.  Code with html output:
        print source, end code block, print html, start code block
    """
    if isinstance(part, (str, unicode)) and iscodefence(part):
        if 'code' in state:
            del state['code']
        else:
            state['code'] = part
        return [part], scope, state
    if isinstance(part, (str, unicode)):
        return [part], scope, state
    if isinstance(part, doctest.Example):
        if valid_statement('_last = ' + part.source):
            code = compile('_last = ' + part.source, '<pymarkdown>', 'single')
            exec(code, scope)
            result = scope.pop('_last')
        else:
            with swap_stdout() as s:
                code = compile(part.source, '<pymarkdown>', 'single')
                exec(code, scope)
            result = s.read().rstrip().strip("'")

        if isassignment(part.source):
            out = [doctest.Example(part.source, '')]
        elif type_key(result) in custom_renderers:
            func = custom_renderers[type_key(type(result))]
            out = [doctest.Example(part.source, '')] + func(result, state)
        elif hasattr(result, '__repr_html__'):
            out = [doctest.Example(part.source, ''),
                   closing_fence(state['code']),
                   result.__repr_html__(),
                   state['code']]
        elif hasattr(result, 'to_html'):
            out = [doctest.Example(part.source, ''),
                   closing_fence(state['code']),
                   result.to_html(),
                   state['code']]
        else:
            if not isinstance(result, str):
                result = repr(result)
            out = [doctest.Example(part.source, result)]
        del scope['__builtins__']
        return out, scope, state

    raise NotImplementedError()


def iscodefence(line):
    return (line.startswith('```')
         or line.startswith('~~~')
         or line.startswith('{%') and 'highlight' in line
         or line.startswith('{%') and 'syntax' in line)


def closing_fence(opener):
    """ Closing pair an an opening fence

    >>> closing_fence('```Python')
    '```'
    """
    if '```' in opener:
        return '```'
    if '~~~' in opener:
        return '~~~'
    if 'highlight' in opener:
        return '{% endhighlight %}'
    if 'syntax' in opener:
        return '{% endsyntax %}'


def separate_fence(part, endl='\n'):
    """ Separate code fences from prose or example sections

        >> separate_fence('Hello\n```python')
        ['Hello', '```python']

        >> separate_fence(doctest.Example('1 + 1', '2\n```'))
        [Example('1 + 1', '2'), '```']
    """
    if isinstance(part, (str, unicode)):
        lines = part.split('\n')
        groups = itertools.groupby(lines, iscodefence)
        return ['\n'.join(group) for _, group in groups]
    if isinstance(part, doctest.Example):
        lines = part.want.rstrip().split('\n')
        fences = list(map(iscodefence, lines))
        if any(fences):
            i = fences.index(True)
            return [doctest.Example(part.source, '\n'.join(lines[:i])),
                    lines[i],
                    '\n'.join(lines[i+1:])]
        else:
            return [part]


def prompt(text):
    """ Add >>> and ... prefixes back into code

    prompt("x + 1")  # doctest: +SKIP
    '>>> x + 1'
    prompt("for i in seq:\n    print(i)")
    '>>> for i in seq:\n...     print(i)'
    """
    return '>>> ' + text.rstrip().replace('\n', '\n... ')


parser = doctest.DocTestParser()

def render_part(part):
    """ Render a part into text """
    if isinstance(part, (str, unicode)):
        return part
    if isinstance(part, doctest.Example):
        result = prompt(part.source)
        if part.want:
            result = result + '\n' + part.want
        return result.rstrip()

def isassignment(line):
    return not not re.match('^\w+\s*=', line)


def valid_statement(source):
    """ Is source a valid statement?

    >>> valid_statement('x = 1')
    True
    >>> valid_statement('x = print foo')
    False
    """
    try:
        compile(source, '', 'single')
        return True
    except SyntaxError:
        return False


@contextmanager
def swap_stdout():
    """ Swap sys.stdout with a StringIO object

    Yields the StringIO object and cleans up afterwards

    >>> with swap_stdout() as s:
    ...      print "Hello!",
    >>> s.read()
    'Hello!'
    """
    s = StringIO()
    old = sys.stdout
    sys.stdout = s

    try:
        yield s
    finally:
        s.pos = 0
        sys.stdout = old


def type_key(typ):
    if not isinstance(typ, type):
        typ = type(typ)
    return '%s.%s' % (typ.__module__, typ.__name__)


def render_bokeh_figure(result, state):
    from bokeh.resources import CDN
    if 'headers' not in state:
        state['headers'] = set()
    state['headers'].update([
        '<script src="%s" async=""></script>' % CDN.js_files[0],
        '<link rel="stylesheet" href="%s" type="text/css"/>' % CDN.css_files[0]
        ])

    from bokeh.embed import components
    script, div = components(result, CDN)
    if 'footers' not in state:
        state['footers'] = list()
    state['footers'].append(script)
    return [closing_fence(state['code']),
            div,
            state['code']]


custom_renderers = {'bokeh.plotting.Figure': render_bokeh_figure}
