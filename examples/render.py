from glob import glob
from pymarkdown import process
import os

fns = sorted([fn for fn in glob('examples/*.md')
                 if 'rendered' not in fn])

for fn in fns:
    with open(fn) as f:
        text = f.read()

    processed = process(text)

    with open(fn.rsplit('.')[0] + '.rendered.md', 'w') as f:
        f.write(processed)
