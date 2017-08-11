#!/usr/bin/env python

from plasTeX import Command, Environment

class xymatrix(Command):
  args = 'str'

  class EndRow(Command):
    """ End of a row """
    macroName = '\\'
