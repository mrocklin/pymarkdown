import doctest

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

    >>> prompt("x + 1")
    '>>> x + 1'
    >>> prompt("for i in seq:\n    print(i)")
    '>>> for i in seq:\n...     print(i)'
    """
    return ('>>> '
            + text.rstrip().replace('\n', '... ')
            + ('\n' if text[-1] == '\n' else ''))


parser = doctest.DocTestParser()


def process(text):
    """ Replace failures in docstring with results """
    text = separate_code_braces(text)
    runner = RecordingDocTestRunner()
    test = parser.get_doctest(text, dict(), 'foo', '', 0)
    runner.run(test)
    parts = parser.parse(text)

    parts2 = []
    events = iter(runner.events)
    for part in parts:
        if isinstance(part, doctest.Example):
            _, _, _, example, result = next(events)
            parts2.append(prompt(example.source))
            if result.rstrip():
                parts2.append(result)
        else:
            if part:
                parts2.append(part)

    return cleanup_code_braces(''.join(parts2))
