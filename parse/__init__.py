import logging
import azure.functions as func
import pandas as pd
import uuid
import json
import datetime
import traceback


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

    df_split = df_split.drop_duplicates().copy()

    return df_split.to_json(orient="index")


def main(req: func.HttpRequest, healthpebble: func.Out[str]) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    # name = req.params.get("name")
    # if not name:
    #     try:
    #         req_body = req.get_json()
    #     except ValueError:
    #         pass
    #     else:
    #         name = req_body.get("name")

    try:
        data = req.params.get("data")
    except:
        logging.info("params get does not work")
    try:
        data = req.values.get("data")
    except:
        logging.info("values get does not work")
    try:
        data = req.form.get("data")
    except:
        logging.info("form get does not work")
    if not data:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            data = req_body.get("data")
    if not data:
        data = "empty"
    logging.info(f"data: {data}")

    try:
        logging.info(f"eval(data): {eval(data)}")
    except:
        err_str = traceback.format_exc()
        logging.info(f"eval(data) not succeded: {err_str}")
        return func.HttpResponse(f"Error: {err_str}", status_code=400,)

    logging.info("Parsing data.")
    try:
        data = parse_data(data)
        logging.info(f"parsed data: {data}")
    except:
        err_str = traceback.format_exc()
        logging.info(f"Parsing of data has not succeded: {err_str}")
        return func.HttpResponse(f"Error: {err_str}", status_code=400,)

    try:
        logging.info("Writing to healthpebble table")
        timestamp = str(datetime.datetime.utcnow())
        data_dic = eval(data)
        rows = []
        for k in data_dic.keys():
            rowKey = str(uuid.uuid4())
            row = {
                "Name": "Output binding message",
                "RowKey": rowKey,
                "timestamp": timestamp,
            }
            for kk in data_dic[k].keys():
                row[kk] = data_dic[k][kk]
            rows.append(row)
        healthpebble.set(json.dumps(rows))
        return func.HttpResponse(
            f"Data from Pebble succesfully parsed and written to table.",
            status_code=200,
        )
    except:
        err_str = traceback.format_exc()
        logging.info(f"Write to table failed: {err_str}")
        return func.HttpResponse(f"Error: {err_str}", status_code=400,)

    # if name:
    #     return func.HttpResponse(f"Hello {name}! This is your data: {data}")
    # else:
    #     err_str = traceback.format_exc()
    #     return func.HttpResponse(
    #         f"Error: {err_str}",
    #         # "Please pass a name on the query string or in the request body",
    #         status_code=400,
    #     )
