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
from plasTeX.DOM import Node

log = plasTeX.Logging.getLogger()

# give the closest theorem environment to this proof
def searchTheorem(linear, proof):
  # last visited node
  last = None

  for current in linear:
    # iterate over the theorems
    if current.nodeName == "thmenv":
      last = current

    # if the proof matches, then return the last visited theorem node
    if current.isSameNode(proof):
      return last.id


class GerbyRenderable(Renderable):
  @property
  def filenameoverride(self):
    # handle tags
    if "tag" in self.userdata:
      environment = self.nodeName
      if self.nodeName == "thmenv":
        environment = self.thmName

      return environment + "-" + self.ref + "-" + self.userdata["tag"] + "-" + self.id

    # handle proofs
    if self.nodeName == "proof":
      # caption can contain a \ref
      if self.attributes["caption"] and len(self.attributes["caption"].getElementsByTagName("ref")) > 0:
        # use the first one for now, in theory there could be more
        label = [ref.attributes["label"] for ref in self.attributes["caption"].getElementsByTagName("ref")][0]
      # just take the closest theorem
      else:
        label = searchTheorem(self.ownerDocument.userdata["linear"], self)

      if label in self.ownerDocument.userdata["labels"]:
        tag = self.ownerDocument.userdata["labels"][label]
        self.ownerDocument.userdata["proofs"][tag] += 1
        return "proof-" + tag + "-" + str(self.ownerDocument.userdata["proofs"][tag])

    raise AttributeError


"""Helper functors for Gerby"""

def decorateTags(node, labels):
  """Recursively decorate labeled nodes with Gerby-specific userdata"""
  if node.nodeType == plasTeX.Macro.ELEMENT_NODE and node.id[0:2] != "a0":
    # plasTeX.Packages.hyperref parses hypertargets, but we ignore them
    if node.nodeName != "hypertarget" and node.id in labels:
      node.userdata["tag"] = labels[node.id]
      node.userdata["propagate"] = True

  if node.nodeName == "proof":
    node.userdata["propagate"] = True

  for child in node.childNodes:
    decorateTags(child, labels)

def loadTags(document):
  """Read the tags file and construct the tags and labels dictionary"""
  with open(document.userdata["working-dir"] + "/" + document.config["gerby"]["tags"]) as f:
    content = f.readlines()

  document.userdata["tags"] = dict()   # tag to label
  document.userdata["labels"] = dict() # label to tag
  document.userdata["proofs"] = dict() # count number of proofs for a tag

  for line in content:
    if line[0] == "#": continue

    (tag, label) = line.rstrip().split(",")
    document.userdata["tags"][tag] = label
    document.userdata["labels"][label] = tag
    document.userdata["proofs"][tag] = 0

def linearRepresentation(document):
  """Make a linear representation of the document containing theorems and proofs"""
  document.userdata["linear"] = list()
  stack = list()

  stack.extend(document.childNodes)

  while len(stack) > 0:
    node = stack.pop()

    if node.nodeName in ["thmenv", "proof"]:
      document.userdata["linear"].append(node)

    stack.extend(node.childNodes)

  document.userdata["linear"] = list(reversed(document.userdata["linear"])) # TODO figure out why this is necessary


class Gerby(_Renderer):
  """ Tag-aware renderer for HTML documents """

  fileExtension = ''
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
    rendererdata = document.rendererdata["gerby"] = dict()
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
    # create the tags and labels dictionaries in the document
    loadTags(document)

    # we decorate all DOM elements with labels that appear in the tags file
    decorateTags(document, document.userdata["labels"])

    # create a linearised version of the document containing theorems and proofs in order
    linearRepresentation(document)

    _Renderer.render(self, document)

Renderer = Gerby
