from enum import Enum


class SexEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class ActivityLevelEnum(str, Enum):
    sedentary = "sedentary"
    light = "light"
    moderate = "moderate"
    active = "active"
    very_active = "very_active"


class FitnessGoalEnum(str, Enum):
    lose = "lose"
    maintain = "maintain"
    gain = "gain"


class ImageUploadStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    complete = "complete"
    failed = "failed"
