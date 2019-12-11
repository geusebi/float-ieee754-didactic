from sys import argv
import re

URL = 'https://gitlab.com/geusebi/float-ieee754-didactic/raw/master/'

if len(argv) != 2:
    raise ValueError(f"Usage: {argv[0]} <out_file>")
out_file = argv[1]

ref_re = re.compile("\[(.+?)]: *(.+?)")
ref_replace = f"[\\1]: {URL}\\2"

img_re = re.compile("!\[(.+?)] *\((.+?)\)")
img_replace = f"![\\1]({URL}\\2)"

with open("README.md", "r") as fh:
    readme = fh.read()

new_readme = ref_re.sub(ref_replace, readme)
new_readme = img_re.sub(img_replace, new_readme)

with open(out_file, "w") as fh:
    fh.write(new_readme)
