import doctest
import os

from pymarkdown.core import (process, parser, step, separate_fence,
        render_bokeh_figure, render_matplotlib_figure)


text = """
Title
=====

Some prose

```
>>> x = 1
>>> x + 1
```
""".strip()

desired = """
Title
=====

Some prose

```
>>> x = 1
>>> x + 1
2
```
""".strip()


def test_process():
    assert process(text) == desired



class Shout(object):
    def __init__(self, data):
        self.data = data

    def __repr_html__(self):
        return "<h1>%s</h1>" % self.data

def test_step():
    out, scope, state = step("prose", {'x': 1}, {})
    assert (out, scope, state) == (["prose"], {'x': 1}, {})

    out, scope, state = step("```Python", {'x': 1}, {})
    assert (out, scope, state) == (["```Python"], {'x': 1}, {'code': '```Python'})

    # Remove code state
    out, scope, state = step("```", {'x': 1}, {'code': '```Python'})
    assert (out, scope, state) == (["```"], {'x': 1}, {})

    a = doctest.Example("x + 1", "3")
    b = doctest.Example("x + 1", "2")
    out, scope, state = step(a, {'x': 1}, {'code': '```Python'})
    assert (out, scope, state) == ([b], {'x': 1}, {'code': '```Python'})

    a = doctest.Example("y = x + 1", "")
    out, scope, state = step(a, {'x': 1}, {'code': '```Python'})
    assert (out, scope, state) == ([a], {'x': 1, 'y': 2}, {'code': '```Python'})

    a = doctest.Example("Shout('Hello!')", '')
    out, scope, state = step(a, {'Shout': Shout}, {'code': '```Python'})
    assert out == [a, '```', Shout('Hello!').__repr_html__(), '```Python']
    assert state == {'code': '```Python'}


    a = doctest.Example("print(5)", '')
    b = doctest.Example("print(5)", '5')
    out, scope, state = step(a, {}, {'code': '```Python'})
    assert (out, scope, state) == ([b], {}, {'code': '```Python'})


def test_separate_fence():
    assert separate_fence('Hello\n```python') == ['Hello', '```python']

    assert separate_fence(doctest.Example('1 + 1', '2\n```')) ==\
            [doctest.Example('1 + 1', '2'), '```', '']


def test_render_bokeh():
    try:
        from bokeh.plotting import figure
    except ImportError:
        return
    p = figure(title='My Title')
    p.line([1, 2, 3], [1, 4, 9])

    state = {'code': '```'}
    out = render_bokeh_figure(p, state)

    assert out[0] == '```'
    assert out[1].startswith('<div')
    assert out[2] == '```'
    assert 'My Title' in state['footers'][0]
    assert any('.css' in header for header in state['headers'])
    assert any('.js' in header for header in state['headers'])


def test_render_matplotlib():
    try:
        from matplotlib import pyplot as plt
    except ImportError:
        return

    fig = plt.figure()

    state = {'code': '```'}
    out = render_matplotlib_figure(fig, state)

    assert out[0] == '```'
    assert out[1].startswith('![')
    assert out[2] == '```'
    assert state['images'][0] in out[1]

    assert os.path.exists('images')
    assert os.path.exists(os.path.join('images', state['images'][0]))
