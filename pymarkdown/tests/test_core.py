from pymarkdown.core import partition_by_blocks, transform_code, render

text = """
Title
=====

Some prose

```
>>> 1 + 1
```
"""

desired = """
Title
=====

Some prose

```
>>> 1 + 1
2
```
"""


def test_partition_by_blocks():
    parts = list(partition_by_blocks(text.split('\n')))
    assert parts[0]['type'] == 'prose'
    assert 'Title' in parts[0]['content']

    assert parts[1]['type'] == 'code'
    assert '>>> 1 + 1' in parts[1]['content']


def test_transform_code():
    lines = ['```', '>>> 1 + 1', '```']
    assert transform_code(lines) == ['```', '>>> 1 + 1', '2', '```']
    lines = ['>>> 1 + 1', '3']
    assert transform_code(lines) == ['>>> 1 + 1', '2']
    lines = ['>>> 1 + 1', '3', '4', '>>> 5']
    assert transform_code(lines) == ['>>> 1 + 1', '2', '>>> 5', '5']
    lines = ['>>> 1 + 1', '3', '4', '', '>>> 5']
    assert transform_code(lines) == ['>>> 1 + 1', '2', '', '>>> 5', '5']


def test_render():
    assert render(text) == desired
