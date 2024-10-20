import ndjson
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class Street(BaseModel):
    number: int
    name: str


class Coordinates(BaseModel):
    latitude: float
    longitude: float


class Timezone(BaseModel):
    offset: str
    description: str


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


class Login(BaseModel):
    uuid: str
    username: str
    password: str
    salt: str
    md5: str
    sha1: str
    sha256: str


class DateAge(BaseModel):
    date: datetime
    age: int


class RecordId(BaseModel):
    name: str
    value: str | None


class Picture(BaseModel):
    large: str
    medium: str
    thumbnail: str


class Record(BaseModel):
    gender: str
    email: str
    phone: str
    cell: str
    nat: str
    name: Name
    location: Location
    login: Login
    dob: DateAge
    registered: DateAge
    id: RecordId
    picture: Picture


def pydantic_check_data(filename: str):
    with open(filename, "rt") as f:
        raw_records = ndjson.load(f)
    records = [Record(**x) for x in raw_records]
    print(records[0])


if __name__ == "__main__":
    pydantic_check_data("records_3.ndjson")
