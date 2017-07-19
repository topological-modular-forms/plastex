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
