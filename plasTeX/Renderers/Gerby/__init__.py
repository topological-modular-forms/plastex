#!/usr/bin/env python


"""
How to test this (for now):
  0) get yourself a copy of the Stacks project repository
  1) put the tags/tags file in the tags/tmp folder (which is populated after running make tags)
  2) comment out all but one reasonably sized chapter in book.tex
  3) run plastex --renderer=Gerby book.tex in tags/tmp
"""

import os, re
import plasTeX
from plasTeX.Renderers.PageTemplate import Renderer as _Renderer
from plasTeX.Renderers import Renderable

log = plasTeX.Logging.getLogger()

# TODO move this to something more reasonable like obj.ownerDocument
with open("tags") as f:
  content = f.readlines()

tags = dict()
labels = dict()

for line in content:
  if line[0] == "#": continue

  (tag, label) = line.rstrip().split(",")
  tags[tag] = label
  labels[label] = tag


class GerbyRenderable(Renderable):
    def __str__(self):
        if hasattr(self, 'id') and not self.id.startswith('a0'):
            log.info("%s has tag %s", self.id, labels[self.id])
        return Renderable.__str__(self)


class Gerby(_Renderer):
  """ Tag-aware renderer for HTML documents """

  fileExtension = '.html'
  imageTypes = ['.png','.jpg','.jpeg','.gif']
  vectorImageTypes = ['.svg']
  renderableClass = GerbyRenderable

  def loadTemplates(self, document):
    """Load templates as in PageTemplate but also look for packages that
    want to override some templates and handles extra css and javascript."""

    try:
      import jinja2
    except ImportError:
      log.error('Jinja2 is not available, hence the HTML5 renderer cannot be used.')

    _Renderer.loadTemplates(self, document)
    rendererdata = document.rendererdata['html5'] = dict()
    config = document.config

    rendererDir = os.path.dirname(__file__)

    srcDir = document.userdata['working-dir']
    buildDir = os.getcwd()


  def cleanup(self, document, files, postProcess=None):
    res = _Renderer.cleanup(self, document, files, postProcess=postProcess)
    return res

  def processFileContent(self, document, s):
    s = _Renderer.processFileContent(self, document, s)

    return s

Renderer = Gerby
