from pymarkdown.core import process

text = """
Title
=====

Some prose

>>> 1 + 1
"""

desired = """
Title
=====

Some prose

>>> 1 + 1
2
"""


def test_process():
    assert process(text) == desired
