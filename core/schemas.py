from ninja import Schema
from uuid import UUID 
from datetime import datetime
import enum
from typing import List

class GenderChoices(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"

class AgeGroupChoices(str, enum.Enum):
    CHILD = 'child'
    TEENAGER = 'teenager'
    ADULT = 'adult'
    SENIOR = 'senior'

class PersonSchema(Schema):
    id: UUID
    name: str 
    gender: GenderChoices 
    gender_probability: float
    sample_size: int 
    age: int 
    age_group: AgeGroupChoices 
    country_id: str
    country_probability: float
    created_at: datetime
     
class CreatePersonSchema(Schema):
    name: str 

class SuccessResponse(Schema):
    status: str
    message: str | None = None
    data: PersonSchema

    class Config:
        from_attrtibutes = True

class SuccessMultipleResponse(Schema):
    status: str
    count: int
    data: List[PersonSchema]

class CountryProb(Schema):
    country_id: str
    probability: float

class GenderResponse(Schema):
    count: int
    gender: str
    probability: float

class AgeResponse(Schema):
    count: int
    age: int

class CountryResponse(Schema):
    count: int
    country: List[CountryProb]

class ErrorResponse(Schema):
    status: int
    message: str

class ApiData(Schema):
    age_data: AgeResponse | None
    gender_data: GenderResponse | None
    country_data: CountryResponse | None

class ApiResult(Schema):
    success: bool
    data: ApiData | None
    error: ErrorResponse | None

