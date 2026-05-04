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
    age: int
    age_group: AgeGroupChoices
    country_id: str
    country_name: str
    country_probability: float
    created_at: datetime

class FilterParams(Schema):
    gender: str | None = None
    age_group: str | None = None
    country_id: str | None = None
    country: str | None = None
    min_age: int | None = None
    max_age: int | None = None
    min_gender_probability: int | float | None = None
    min_country_probability: int | float | None = None
    sort_by: str | None = None
    order: str | None = None
    page: int | None = 1
    limit: int | None = 10

class CreatePersonSchema(Schema):
    name: str

class SuccessResponse(Schema):
    status: str
    message: str | None = None
    data: PersonSchema

    class Config:
        from_attrtibutes = True

class LinksSchema(Schema):
    self: str
    next: str
    prev: str

class SuccessMultipleResponse(Schema):
    status: str
    page: int
    limit: int
    total: int
    total_pages: int
    links: LinksSchema
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
