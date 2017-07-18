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


# Support for Jinja2 templates
try:
  from jinja2 import Environment, contextfunction
except ImportError:
  def jinja2template(s, encoding='utf8'):
    def renderjinja2(obj):
      return s
    return renderjinja2
else:
  try:
    import ipdb as pdb
  except ImportError:
    import pdb

  @contextfunction
  def debug(context):
    pdb.set_trace()

  def gerbyJinja2(s, encoding='utf8'):
    env = Environment(trim_blocks=True, lstrip_blocks=True)
    env.globals['debug'] = debug

    def renderjinja2(obj, s=s):
      tvars = {'here':obj,
               'obj':obj,
               'container':obj.parentNode,
               'config':obj.ownerDocument.config,
               'context':obj.ownerDocument.context,
               'templates':obj.renderer}

      if obj.id[0:2] != "a0":
        log.info("%s has tag %s", obj.id, labels[obj.id])

      tpl = env.from_string(s)
      return tpl.render(tvars)

    return renderjinja2

class Gerby(_Renderer):
  """ Tag-aware renderer for HTML documents """

  fileExtension = '.html'
  imageTypes = ['.png','.jpg','.jpeg','.gif']
  vectorImageTypes = ['.svg']

  def loadTemplates(self, document):
    """Load templates as in PageTemplate but also look for packages that
    want to override some templates and handles extra css and javascript."""

    try:
      import jinja2
    except ImportError:
      log.error('Jinja2 is not available, hence the HTML5 renderer cannot be used.')

    self.registerEngine('jinja2', None, '.jinja2', gerbyJinja2)

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

    # remove empty paragraphs
    s = re.compile(r'<p>\s*</p>', re.I).sub(r'', s)

    return s

  def render(self, document):
    # we decorate all DOM elements with labels that appear in the tags file
    def decorateTags(node):
      if node.nodeType == plasTeX.Macro.ELEMENT_NODE and node.id[0:2] != "a0":
        # plasTeX.Packages.hyperref parses hypertargets, but we ignore them
        if node.nodeName != "hypertarget":
          node.tag = labels[node.id]

      for child in node.childNodes: decorateTags(child)

    decorateTags(document)

    _Renderer.render(self, document)

Renderer = Gerby
