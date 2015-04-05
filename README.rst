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
    >>> 1 + 1

    >>> 2 + 2
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
    >>> 1 + 1
    2

    >>> 2 + 2
    4
    ```
