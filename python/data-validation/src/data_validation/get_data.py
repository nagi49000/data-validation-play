import requests
import ndjson
import pandas as pd
import pandera as pa
import pandera.io
from datetime import datetime, UTC


def get_random_users_from_api(n_record: int, filename: str | None = None) -> list[dict]:
    random_users = []
    for _ in range(n_record):
        response = requests.get("https://randomuser.me/api/")
        records = response.json()["results"]
        random_users += records
    if filename:
        with open(filename, "wt") as f:
            ndjson.dump(random_users, f)
    return random_users


def get_pandas_df_from_file(filename: str) -> pd.DataFrame:
    df = pd.read_json(filename, lines=True)
    # expand out nested fields
    for struct_col in [
        "name",
        "location",
        "login",
        "dob",
        "registered",
        "id",
        "picture",
        "location_street",
        "location_coordinates",
        "location_timezone",
    ]:
        df = pd.concat(
            [
                # drop the original column
                df.drop([struct_col], axis=1),
                # take the original column and apply Series to expand out the dict,
                # and concat with the dataframe (with original column dropped)
                df[struct_col].apply(pd.Series).add_prefix(f"{struct_col}_")
            ],
            axis=1
        )

    # cast fields that may be read in wrong
    df["location_coordinates_latitude"] = df["location_coordinates_latitude"].astype(float)
    df["location_coordinates_longitude"] = df["location_coordinates_longitude"].astype(float)
    df["location_postcode"] = df["location_postcode"].astype(str)
    df["dob_date"] = pd.to_datetime(df["dob_date"])
    df["registered_date"] = pd.to_datetime(df["registered_date"])

    return df


def write_validation_schema(yaml_name: str):
    phone_no_regex = r"^[\+]?[(]?[0-9]{2,4}[)]?[-\s\.]?[0-9]{3,4}[-\s\.]?[0-9]{3,6}$"
    email_address_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    timezone_offset_regex = r"^([+|-])?[0-9]{1,2}:[0-9]{2}$"
    url_regex = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"

    schema = pa.DataFrameSchema(
        columns={
            "gender": pa.Column(str, pa.Check.isin(["male", "female"])),
            "email": pa.Column(str, pa.Check.str_matches(email_address_regex)),
            "phone": pa.Column(str, pa.Check.str_matches(phone_no_regex)),
            "cell": pa.Column(str, pa.Check.str_matches(phone_no_regex)),
            "nat": pa.Column(str, pa.Check.str_length(min_value=2, max_value=2)),
            "name_title": pa.Column(str, pa.Check.isin(["Mr", "Mrs", "Ms", "Miss", "Mademoiselle", "Madame", "Monsieur"])),
            "name_first": pa.Column(str),
            "name_last": pa.Column(str),
            "location_city": pa.Column(str),
            "location_state": pa.Column(str),
            "location_country": pa.Column(str),
            "location_postcode": pa.Column(str),
            "login_uuid": pa.Column(str),
            "login_username": pa.Column(str),
            "login_password": pa.Column(str),
            "login_salt": pa.Column(str),
            "login_md5": pa.Column(str),
            "login_sha1": pa.Column(str),
            "login_sha256": pa.Column(str),
            "dob_date": pa.Column(datetime, pa.Check.in_range(datetime(1940, 1, 1, tzinfo=UTC), datetime(2030, 1, 1, tzinfo=UTC))),
            "dob_age": pa.Column(int, pa.Check.in_range(0, 100)),
            "registered_date": pa.Column(datetime, pa.Check.in_range(datetime(1990, 1, 1, tzinfo=UTC), datetime(2030, 1, 1, tzinfo=UTC))),
            "registered_age": pa.Column(int, pa.Check.in_range(0, 100)),
            "id_name": pa.Column(str),
            "id_value": pa.Column(str, nullable=True),
            "picture_large": pa.Column(str, pa.Check.str_matches(url_regex)),
            "picture_medium": pa.Column(str, pa.Check.str_matches(url_regex)),
            "picture_thumbnail": pa.Column(str, pa.Check.str_matches(url_regex)),
            "location_street_number": pa.Column(int, pa.Check.in_range(1, 99999)),
            "location_street_name": pa.Column(str),
            "location_coordinates_latitude": pa.Column(float, pa.Check.in_range(-90.0, 90.0)),
            "location_coordinates_longitude": pa.Column(float, pa.Check.in_range(-180.0, 180.0)),
            "location_timezone_offset": pa.Column(str, pa.Check.str_matches(timezone_offset_regex)),
            "location_timezone_description": pa.Column(str),
        }
    )

    with open(yaml_name, "wt") as f:
        pandera.io.to_yaml(schema, f)
    with open(yaml_name, "rt") as f:
        lines = f.readlines()
    # update the datetimes in the yaml for timezone. TODO - work out how to do this in code above
    lines = [x.replace("dtype: datetime64[ns]", "dtype: datetime64[ns, UTC]") for x in lines]
    with open(yaml_name, "wt") as f:
        f.writelines(lines)


def validate_pandas_df(df: pd.DataFrame, schema_yaml_filename: str):
    schema = pandera.io.from_yaml(schema_yaml_filename)
    try:
        schema.validate(df, lazy=True)
    except pa.errors.SchemaErrors as exc:
        print("Schema errors and failure cases:")
        print(exc.failure_cases.to_string())


if __name__ == "__main__":
    df = get_pandas_df_from_file("records.ndjson")
    write_validation_schema("pandera-randomuser-schema.yml")
    validate_pandas_df(df, "pandera-randomuser-schema.yml")
