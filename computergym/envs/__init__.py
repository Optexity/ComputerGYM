from enum import Enum, unique

from .browser.openended_website import OpenEndedWebsite


@unique
class EnvTypes(Enum):
    browser = "browser"
    computer = "computer"


class BrowserEnvTypes(Enum):
    openended = "openended"
    workarena = "workarena"
