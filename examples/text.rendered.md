Title
=====

Some prose


```Python
# And some code

>>> x = 1
>>> x + 1
2


>>> 2 + 2*x
4
```

We also handle HTML with `__repr_html__`

```Python
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
```Python
```