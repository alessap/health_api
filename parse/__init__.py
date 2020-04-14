import logging
import azure.functions as func
import pandas as pd


# example data "2020-04-11T03:11:00Z,0,13,7,0,1,0,0"
# example data "2020-04-11T03:11:00Z,0,13,7,0,1,0,0\n2020-04-11T03:43:00Z,0,0,4,1423,1,0,0"
def parse_data(data):
    columns = [
        "measurement_time_UTC",
        "steps",
        "yaw",
        "pitch",
        "VMC",
        "light",
        "activity_mask",
        "heart_beat_bpm",
    ]
    dfdata = {"raw_data": [str(data)]}
    df = pd.DataFrame(dfdata)
    df = (
        df.join(
            pd.DataFrame(
                df.raw_data.str.split("\n", expand=True)
                .stack()
                .reset_index(level=1, drop=True),
                columns=["raw_data "],
            )
        )
        .drop("raw_data", 1)
        .rename(columns=str.strip)
        .reset_index(drop=True)
        .copy()
    )

    df_split = df.raw_data.str.split(",", expand=True)
    df_split.columns = columns
    df_split = df_split.replace({"": None})
    for col in [i for i in df_split.columns if i != "measurement_time_UTC"]:
        df_split[col] = df_split[col].astype(float)
        df_split[col] = df_split[col].astype(pd.Int64Dtype())

    df_split.measurement_time_UTC = pd.to_datetime(df_split.measurement_time_UTC)
    df_split = df_split.sort_values(by="measurement_time_UTC")
    df_split = df_split.drop_duplicates().copy()

    return df_split.to_json()


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    name = req.params.get("name")
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get("name")

    data = req.params.get("data")
    if not data:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            data = req_body.get("data")
    if not data:
        data = "empty"

    logging.info("Parsing data.")
    try:
        data = parse_data(data)
    except:
        logging.error("Parsing of data has not succeded.")
        data = data

    if name:
        return func.HttpResponse(f"Hello {name}! This is your data: {data}")
    else:
        return func.HttpResponse(
            "Please pass a name on the query string or in the request body",
            status_code=400,
        )
