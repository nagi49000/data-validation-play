import re
import ndjson
from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
    ValidationError
)
from datetime import datetime, UTC


phone_no_regex = r"^[\+]?[(]?[0-9]{2,4}[)]?[-\s\.]?[0-9]{3,4}[-\s\.]?[0-9]{3,6}$"
email_address_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
timezone_offset_regex = r"^([+|-])?[0-9]{1,2}:[0-9]{2}$"
url_regex = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"


class Street(BaseModel):
    number: int
    name: str

    @field_validator("number")
    @classmethod
    def age_is_in_range(cls, v: int) -> int:
        min_value = 0
        max_value = 99999
        if min_value < v < max_value:
            return v
        else:
            raise ValueError("must be in range [{min_value}, {max_value}]")


class Coordinates(BaseModel):
    latitude: float
    longitude: float

    @field_validator("latitude")
    @classmethod
    def latitude_is_in_range(cls, v: float) -> float:
        min_value = -90.0
        max_value = 90.0
        if min_value < v < max_value:
            return v
        else:
            raise ValueError("must be in range [{min_value}, {max_value}]")

    @field_validator("longitude")
    @classmethod
    def longitude_is_in_range(cls, v: float) -> float:
        min_value = -180.0
        max_value = 180.0
        if min_value < v < max_value:
            return v
        else:
            raise ValueError("must be in range [{min_value}, {max_value}]")


class Timezone(BaseModel):
    offset: str
    description: str

    @field_validator("offset")
    @classmethod
    def offset_obeys_regex(cls, v: str) -> str:
        if re.match(timezone_offset_regex, v):
            return v
        else:
            raise ValueError("failed regex check")


class Location(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)
    city: str
    state: str
    country: str
    postcode: str  # sometimes is an int in the data
    street: Street
    coordinates: Coordinates
    timezone: Timezone


class Name(BaseModel):
    title: str
    first: str
    last: str

    @field_validator("title")
    @classmethod
    def from_allow_list(cls, v: str) -> str:
        allow_list = {"Mr", "Mrs", "Ms", "Miss", "Mademoiselle", "Madame", "Monsieur"}
        if v not in allow_list:
            raise ValueError(f"must be in {allow_list}")
        return v


class Login(BaseModel):
    uuid: str
    username: str
    password: str
    salt: str
    md5: str
    sha1: str
    sha256: str


class Dob(BaseModel):
    date: datetime
    age: int

    @field_validator("date")
    @classmethod
    def date_is_in_range(cls, v: datetime) -> datetime:
        min_value = datetime(1940, 1, 1, tzinfo=UTC)
        max_value = datetime(2030, 1, 1, tzinfo=UTC)
        if min_value < v < max_value:
            return v
        else:
            raise ValueError("must be in range [{min_value}, {max_value}]")

    @field_validator("age")
    @classmethod
    def age_is_in_range(cls, v: int) -> int:
        min_value = 0
        max_value = 100
        if min_value < v < max_value:
            return v
        else:
            raise ValueError("must be in range [{min_value}, {max_value}]")


class Registered(BaseModel):
    date: datetime
    age: int

    @field_validator("date")
    @classmethod
    def date_is_in_range(cls, v: datetime) -> datetime:
        min_value = datetime(1990, 1, 1, tzinfo=UTC)
        max_value = datetime(2030, 1, 1, tzinfo=UTC)
        if min_value < v < max_value:
            return v
        else:
            raise ValueError("must be in range [{min_value}, {max_value}]")

    @field_validator("age")
    @classmethod
    def age_is_in_range(cls, v: int) -> int:
        min_value = 0
        max_value = 100
        if min_value < v < max_value:
            return v
        else:
            raise ValueError("must be in range [{min_value}, {max_value}]")


class RecordId(BaseModel):
    name: str
    value: str | None


class Picture(BaseModel):
    large: str
    medium: str
    thumbnail: str

    @field_validator("large", "medium", "thumbnail")
    @classmethod
    def all_obeys_regex(cls, v: str) -> str:
        if re.match(url_regex, v):
            return v
        else:
            raise ValueError("failed regex check")


class Record(BaseModel):
    gender: str
    email: str
    phone: str
    cell: str
    nat: str
    name: Name
    location: Location
    login: Login
    dob: Dob
    registered: Registered
    id: RecordId
    picture: Picture

    @field_validator("gender")
    @classmethod
    def gender_from_allow_list(cls, v: str) -> str:
        allow_list = {"male", "female"}
        if v not in allow_list:
            raise ValueError(f"must be in {allow_list}")
        return v

    @field_validator("nat")
    @classmethod
    def nat_is_correct_length(cls, v: str) -> str:
        if len(v) != 2:
            raise ValueError("must be of length 2")
        return v

    @field_validator("email")
    @classmethod
    def email_obeys_regex(cls, v: str) -> str:
        if re.match(email_address_regex, v):
            return v
        else:
            raise ValueError("failed regex check")

    """
    @field_validator("phone", "cell")
    @classmethod
    def phone_cell_obeys_regex(cls, v: str) -> str:
        if re.match(phone_no_regex, v):
            return v
        else:
            raise ValueError("failed regex check")
    """


def pydantic_check_data(filename: str):
    with open(filename, "rt") as f:
        raw_records = ndjson.load(f)
    for raw_record in raw_records:
        try:
            _ = Record(**raw_record)
        except ValidationError as exc:
            print(exc)


if __name__ == "__main__":
    pydantic_check_data("records_3.ndjson")
