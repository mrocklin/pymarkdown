PyMarkdown
==========

Evaluate code in markdown.

Why?
----

Mostly because I was jealous of RMarkdown/knitr.

Interleaving prose, code, and results conveys meaning well.  The Jupyter
notebook taught us this.  When we author static content we want a simple
text-based format. Markdown is good here because it plays well with other tools
(`vi/emacs`, `pandoc`, `git`.)  RMarkdown/knitr has demonstrated value in the R
ecosystem, pymarkdown just copies that idea (badly at the moment.)

How does this work?
-------------------

PyMarkdown leverages the `doctest` module to parse code into prose and code
segments much like a docstring.  We then execute each code segment in order
with `exec`, tracking state throughout the document, emitting or correcting
results from computation where appropriate.  Both input and output documents
are valid markdown appropriate for publishing on github, your favorite
blogging software, or pandoc.


Example
-------

### Input

    Our documents contain prose with *rich formatting*.

    ```Python
    # And code blocks
    >>> x = 1
    >>> x + 1

    >>> 2 + 2*x
    with potentially missing or wrong results
    ```

We run pymarkdown:

    $ pymarkdown text.md text.out.md

### Output

Our documents contain prose with *rich formatting*.

```Python
# And code blocks
>>> x = 1
>>> x + 1
2

>>> 2 + 2*x
4
```

Fancy Support
-------------

    ### HTML

    PyMarkdown leverages standard protocols like `to_html` or `__repr_html__`.

    ```python
    >>> import pandas as pd
    >>> df = pd.DataFrame({'name': ['Alice', 'Bob', 'Charlie'],
    ...                    'balance': [100, 200, 300]})
    >>> df
    ```

### HTML

PyMarkdown leverages standard protocols like `to_html` or `__repr_html__`.

```python
>>> import pandas as pd
>>> df = pd.DataFrame({'name': ['Alice', 'Bob', 'Charlie'],
...                    'balance': [100, 200, 300]})
>>> df
```
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>balance</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td> 100</td>
      <td>   Alice</td>
    </tr>
    <tr>
      <th>1</th>
      <td> 200</td>
      <td>     Bob</td>
    </tr>
    <tr>
      <th>2</th>
      <td> 300</td>
      <td> Charlie</td>
    </tr>
  </tbody>
</table>


### TODO

* Interact with matplotlib (figure out how IPython does this)
* Interact with Bokeh plots.  These already implement `__repr_html__` so this
  probably just means linking to some static content somewhere.
* Support inlining of values in prose blocks
* Support options like ignore, echo=False, etc..
* Handle exceptions
