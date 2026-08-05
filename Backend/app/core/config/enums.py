from enum import Enum


class Environment(str, Enum):
    """
    Application environment types.
    """

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class HTTPMethod(str, Enum):
    """
    Standard HTTP methods.
    """

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class SortOrder(str, Enum):
    """
    Standard sorting orders.
    """

    ASCENDING = "asc"
    DESCENDING = "desc"


class StatusPlaceholder(str, Enum):
    """
    Placeholder for future entity statuses.
    """

    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    DELETED = "deleted"
