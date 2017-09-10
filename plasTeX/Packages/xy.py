#!/usr/bin/env python

from plasTeX import NoCharSubCommand, Command

class xymatrix(NoCharSubCommand):
  args = 'str'

  class EndRow(Command):
    """ End of a row """
    macroName = '\\'
