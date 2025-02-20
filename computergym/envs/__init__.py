from enum import Enum, unique


@unique
class EnvTypes(Enum):
    browser = "browser"
    computer = "computer"
