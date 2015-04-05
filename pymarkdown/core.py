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

    return ''.join(parts2)
