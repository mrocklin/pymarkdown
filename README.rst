PyMarkdown
==========

Evaluate code in markdown.

Example
-------

Text before::

    Title
    =====

    Some prose


    ```
    # And some code
    >>> x = 1
    >>> x + 1

    >>> 2 + 2*x
    wrong result
    ```

Run pymarkdown::

   $ pymarkdown text.md

Text after::

    Title
    =====

    Some prose


    ```
    # And some code
    >>> x = 1
    >>> x + 1
    2

    >>> 2 + 2*x
    4
    ```
