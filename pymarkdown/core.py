import doctest
import re
from contextlib import contextmanager
from StringIO import StringIO
import itertools
import sys
from toolz.curried import pipe, map, filter, concat

class RecordingDocTestRunner(doctest.DocTestRunner):
    def __init__(self, *args, **kwargs):
        self.events = list()
        doctest.DocTestRunner.__init__(self, *args, **kwargs)

    def report_failure(self, out, test, example, got):
        self.events.append(('failure', out, test, example, got))
        return doctest.DocTestRunner.report_failure(self, out, test, example, got)
    def report_success(self, out, test, example, got):
        self.events.append(('success', out, test, example, got))
        return doctest.DocTestRunner.report_success(self, out, test, example, got)
    def report_unexpected_exception(self, out, test, example, got):
        self.events.append(('exception', out, test, example, got))
        return doctest.DocTestRunner.report_unexpected_exception(self, out, test, example, got)


def iscodebrace(line):
    return (line.startswith('```')
         or line.startswith('~~~')
         or line.startswith('{%') and 'highlight' in line
         or line.startswith('{%') and 'syntax' in line)


def closing_brace(opener):
    """

    >>> closing_brace('```Python')
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
    """ Separate code braces from prose or example sections

    >>> separate_fence('Hello\n```python')
    ['Hello', '```python']

    >>> separate_fence(doctest.Example('1 + 1', '2\n```'))
    [Example('1 + 1', '2'), '```']
    """
    if isinstance(part, (str, unicode)):
        lines = part.split('\n')
        groups = itertools.groupby(lines, iscodebrace)
        return ['\n'.join(group) for _, group in groups]
    if isinstance(part, doctest.Example):
        lines = part.want.rstrip().split('\n')
        braces = list(map(iscodebrace, lines))
        if any(braces):
            i = braces.index(True)
            return [doctest.Example(part.source, '\n'.join(lines[:i])),
                    lines[i],
                    '\n'.join(lines[i+1:])]
        else:
            return [part]


def prompt(text):
    """

        prompt("x + 1")  # doctest: +SKIP
        '>>> x + 1'
        prompt("for i in seq:\n    print(i)")
        '>>> for i in seq:\n...     print(i)'
    """
    return '>>> ' + text.rstrip().replace('\n', '\n... ')


parser = doctest.DocTestParser()

def render_part(part):
    if isinstance(part, (str, unicode)):
        return part
    if isinstance(part, doctest.Example):
        result = prompt(part.source)
        if part.want:
            result = result + '\n' + part.want
        return result.rstrip()


def process(text):
    """ Replace failures in docstring with results """
    parts = pipe(text, parser.parse,
                       filter(None),
                       map(separate_fence),
                       concat, list)

    scope = dict()
    state = dict()

    out_parts = list()
    for part in parts:
        out, scope, state = step(part, scope, state)
        out_parts.extend(out)

    return pipe(out_parts, map(render_part),
                           filter(None),
                           '\n'.join)


def isassignment(line):
    return not not re.match('^\w+\s*=', line)


def step(part, scope, state):
    """ Step through one part of the document

    1.  Prose: pass through
    2.  Code fence: record
    3.  Code: evaluate
    4.  Code with html output:
        print source, end code block, print html, start code block
    """
    if isinstance(part, (str, unicode)) and iscodebrace(part):
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
        elif hasattr(result, '__repr_html__'):
            out = [doctest.Example(part.source, ''),
                   closing_brace(state['code']),
                   result.__repr_html__(),
                   state['code']]
        elif hasattr(result, 'to_html'):
            out = [doctest.Example(part.source, ''),
                   closing_brace(state['code']),
                   result.to_html(),
                   state['code']]
        else:
            if not isinstance(result, str):
                result = repr(result)
            out = [doctest.Example(part.source, result)]
        del scope['__builtins__']
        return out, scope, state

    raise NotImplementedError()


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
