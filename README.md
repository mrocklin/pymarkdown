PyMarkdown
==========

Evaluate code in markdown.

How does this work?
-------------------

The `doctest` module parses code into prose and code segments.  We then execute
each code segment in order, tracking state throughout the document, emitting or
correcting results from computation where appropriate.


Example
-------

### Input

    Some prose

    ```Python
    # And some code
    >>> x = 1
    >>> x + 1

    >>> 2 + 2*x
    with wrong results
    ```

Run pymarkdown

    $ pymarkdown text.md text.out.md

### Result

Some prose

```Python
# And some code
>>> x = 1
>>> x + 1
2

>>> 2 + 2*x
4
```

Fancy Support
-------------

    ### HTML

    This supports objects that implement `to_html` or `__repr_html__`.
    Lets see an example with Pandas

    ```python
    >>> import pandas as pd
    >>> df = pd.DataFrame({'name': ['Alice', 'Bob', 'Charlie'],
    ...                    'balance': [100, 200, 300]})
    >>> df
    ```

### HTML

This supports objects that implement the `to_html` or `__repr_html__`.
Lets see an example with Pandas

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
