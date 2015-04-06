from glob import glob
from pymarkdown import process
import os

fns = sorted([fn for fn in glob('examples/*.md')
                 if 'rendered' not in fn])

for fn in fns:
    with open(fn) as f:
        text = f.read()

    processed = process(text)

    rendered_fn = fn.rsplit('.', 1)[0] + '.rendered.md'
    with open(rendered_fn, 'w') as f:
        f.write(processed)

    html_fn = fn.rsplit('.', 1)[0] + '.html'
    os.popen('pandoc %s -o %s --standalone' % (rendered_fn, html_fn)).read()
