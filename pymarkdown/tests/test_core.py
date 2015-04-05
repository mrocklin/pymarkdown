from pymarkdown.core import process, separate_code_braces

text = """
Title
=====

Some prose

```
>>> 1 + 1
```
""".rstrip()

desired = """
Title
=====

Some prose

```
>>> 1 + 1
2
```
""".rstrip()


def test_process():
    assert process(text) == desired


def test_separate_code_braces():
    assert separate_code_braces(text).split('\n')[-2:] == ['', '```']
