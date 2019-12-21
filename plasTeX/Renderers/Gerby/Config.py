import os
from plasTeX.ConfigManager import *

config = ConfigManager()

section = config.add_section("gerby")

config.add_category("gerby", "Gerby renderer options")

section["tags"] = StringOption(
  """Location of the tags file""",
  options = "--tags",
  category = "gerby",
  default = "tags",
)

section['tikz-compiler'] = StringOption(
    """ LaTeX compiler for TikZ pictures """,
    options='--tikz-compiler',
    category='gerby',
    default='pdflatex',
)

section['tikz-converter'] = StringOption(
    """ PDF to SVG converter for tikz and tikz-cd """,
    options='--tikz-converter',
    category='gerby',
    default='pdf2svg',
)

section['tikz-template'] = StringOption(
    """ Jinja2 template file for tikz """,
    options='--tikz-template',
    category='gerby',
    default='',
)

section['tikz-cd-template'] = StringOption(
    """ Jinja2 template file for tikz-cd """,
    options='--tikz-cd-template',
    category='gerby',
    default='',
)
