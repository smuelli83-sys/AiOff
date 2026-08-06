from enum import Enum


class ProviderType(str, Enum):

    CORE = "core"

    AI = "ai"

    INFRASTRUCTURE = "infrastructure"

    SECURITY = "security"

    EXTENSION = "extension"
