import doctest
import re
from contextlib import contextmanager
from StringIO import StringIO
import sys

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


def separate_code_braces(text, endl='\n'):
    """ Add endlines before and after code lines

    The doctest parser pulls them into the tests otherwise
    """
    lines = text.rstrip().split(endl)
    out = list()
    for line in lines:
        if iscodebrace(line):
            out.append('')
        out.append(line)
    return endl.join(out)

def cleanup_code_braces(text, endl='\n'):
    """ Remove unnecessary whitespace before/after code braces

    See also:
        sseparate_code_braces
    """
    lines = text.split(endl)
    out = list()
    for line in lines:
        if iscodebrace(line) and out and not out[-1]:
            out.pop()
        out.append(line)
    return endl.join(out)


def prompt(text):
    """

        prompt("x + 1")  # doctest: +SKIP
        '>>> x + 1'
        prompt("for i in seq:\n    print(i)")
        '>>> for i in seq:\n...     print(i)'
    """
    return ('>>> '
            + text.rstrip().replace('\n', '... ')
            + ('\n' if text[-1] == '\n' else ''))


parser = doctest.DocTestParser()

def render_part(part):
    if isinstance(part, str):
        return part
    if isinstance(part, doctest.Example):
        return prompt(part.source) + part.want


def process(text):
    """ Replace failures in docstring with results """
    text = separate_code_braces(text)
    parts = parser.parse(text)

    scope = dict()
    state = dict()

    out_parts = list()
    for part in parts:
        out, scope, state = step(part, scope, state)
        out_parts.extend(out)

    return cleanup_code_braces(''.join(map(render_part, out_parts)))


def isassignment(line):
    return not not re.match('^\w+\s*=', line)


def step(part, scope, state):
    """ Step through one part of the document

    1.  Prose: passed through
    2.  Code fence: recorded
    3.  Code: evaluated
    """
    if isinstance(part, str) and iscodebrace(part):
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
            result = ''
        if hasattr(result, '__repr_html__'):
            out = [closing_brace(state['code']),
                   result.__repr_html__(),
                   state['code']]
        else:
            if result and not isinstance(result, str):
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
