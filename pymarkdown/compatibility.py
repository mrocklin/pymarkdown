import sys

if sys.version_info[0] == 3:
    from io import StringIO
    unicode = str

if sys.version_info[0] == 2:
    from StringIO import StringIO
    unicode = unicode
