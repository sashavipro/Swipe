"""src/core/enum.py."""

import enum


class DealStatus(str, enum.Enum):
    """Deal status."""

    PENDING = "pending"
    ACTIVE = "active"
    SOLD = "sold"
    ARCHIVED = "archived"
    REJECTED = "rejected"


class RequestStatus(str, enum.Enum):
    """Status of request to add to chessboard."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class RoomCount(str, enum.Enum):
    """Number of rooms."""

    STUDIO = "studio"
    ONE = "1"
    TWO = "2"
    THREE = "3"
    FOUR_PLUS = "4+"


class CommunicationMethod(str, enum.Enum):
    """Communication method."""

    CALL = "call"
    MESSAGE = "message"
    ANY = "any"


class LayoutType(str, enum.Enum):
    """Layout type."""

    ISOLATED = "isolated"
    ADJACENT = "adjacent"
    STUDIO = "studio"


class HouseType(str, enum.Enum):
    """House type."""

    MONOLITHIC = "monolithic"
    PANEL = "panel"
    BRICK = "brick"
    BLOCK = "block"


class HouseClass(str, enum.Enum):
    """Housing class."""

    ECONOMY = "economy"
    COMFORT = "comfort"
    BUSINESS = "business"
    ELITE = "elite"


class ConstructionTechnology(str, enum.Enum):
    """Construction technology."""

    MONOLITH = "monolith"
    BRICK = "brick"


class TerritoryType(str, enum.Enum):
    """Territory type."""

    CLOSED = "closed"
    OPEN = "open"


class Utilities(str, enum.Enum):
    """Utilities."""

    CENTRAL = "central"
    AUTONOMOUS = "autonomous"


class GasType(str, enum.Enum):
    """Gas supply."""

    MAIN = "main"
    NONE = "none"


class HeatingType(str, enum.Enum):
    """Heating type."""

    CENTRAL = "central"
    GAS = "gas"
    ELECTRIC = "electric"


class SewerageType(str, enum.Enum):
    """Sewerage type."""

    CENTRAL = "central"
    SEPTIC = "septic"


class WaterSupplyType(str, enum.Enum):
    """Water supply type."""

    CENTRAL = "central"
    WELL = "well"


class Purpose(str, enum.Enum):
    """Property purpose."""

    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"


class PurchaseTerms(str, enum.Enum):
    """Purchase terms."""

    MORTGAGE = "mortgage"
    CASH = "cash"
    INSTALLMENT = "installment"
    MATERNAL_CAPITAL = "maternal_capital"


class Condition(str, enum.Enum):
    """Renovation condition."""

    RENOVATED = "renovated"
    DESIGNER = "designer"
    ROUGH = "rough"
    WHITE_BOX = "white_box"
    NEEDS_REPAIR = "needs_repair"


class PropertyType(str, enum.Enum):
    """Real estate property type."""

    SECONDARY = "secondary"
    NEW_BUILDINGS = "new buildings"
    COTTAGE = "cottage"


class ConstructionStatus(str, enum.Enum):
    """Construction status."""

    READY = "ready"
    NOT_READY = "not ready"


class UserRole(str, enum.Enum):
    """User roles."""

    # pylint: disable=too-few-public-methods

    USER = "user"
    AGENT = "agent"
    DEVELOPER = "developer"
    MODERATOR = "moderator"
    NOTARY = "notary"


class NotificationType(str, enum.Enum):
    """Notification types."""

    # pylint: disable=too-few-public-methods

    ME = "me"
    ME_AND_AGENT = "me_and_agent"
    AGENT = "agent"
    OFF = "off"


class ComplaintReason(str, enum.Enum):
    """Complaint reasons."""

    # pylint: disable=too-few-public-methods

    SPAM = "spam"
    SCAM = "scam"
    INSULT = "insult"
    OTHER = "other"
