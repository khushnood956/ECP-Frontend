import enum


class UserRole(str, enum.Enum):
    STUDENT = "student"
    AGENCY = "agency"
    ADMIN = "admin"


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    IN_PROGRESS = "in_progress"
    WON = "won"
    LOST = "lost"


class AgencyVerificationStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class DegreeLevel(str, enum.Enum):
    HIGH_SCHOOL = "high_school"
    BACHELOR = "bachelor"
    MASTER = "master"
    PHD = "phd"
    POSTDOC = "postdoc"
    OTHER = "other"


class FundingType(str, enum.Enum):
    FULLY_FUNDED = "fully_funded"
    PARTIAL = "partial"
    TUITION_FEE_ONLY = "tuition_fee_only"
    SELF_FUNDED = "self_funded"
