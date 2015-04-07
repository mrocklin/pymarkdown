from __future__ import print_function, absolute_import, unicode_literals

import sys


_str = str
if sys.version.startswith('3'):
	str = _str
else:
	str = unicode


def is_string(obj):
	return isinstance(obj, (_str, str))
