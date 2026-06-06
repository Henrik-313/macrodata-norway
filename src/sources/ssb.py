import itertools

import pandas as pd
import requests


def get_available_tables(
    query: str, pages=30, raw=False
) -> dict[str, any] | list[list[str]]:
    """
    Function that searches for SSB tables based on a keyword. Limited to 30 pages per search.

    Returns table label, id and date updated as default.

    Set raw to True to return the response in raw json format
    Returns response in json format

    Response keys: dict_keys(['language', 'tables', 'page', 'links'])
    Response tables keys: dict_keys(['id', 'label', 'description', 'sortCode', 'updated', 'firstPeriod', 'lastPeriod', 'category', 'variableNames', 'source', 'subjectCode', 'timeUnit', 'paths', 'links'])
    """
    url = f"https://data.ssb.no/api/pxwebapi/v2/tables?query={query}&includeDiscontinued=false&pagesize={pages}"

    response = requests.get(url)

    data = response.json()
    if raw:
        return data

    keys = ["label", "id", "updated"]

    to_return = [list(map(table.get, keys)) for table in data["tables"]]

    return to_return


def fetch_data_and_metadata(tableid: str) -> dict:
    """
    Returns dict with a dataframe and the table metadata

    Info:
    JSON-stat bruker metoden Row-major-order for lagring av data
    """
    response = requests.get(
        f"https://data.ssb.no/api/pxwebapi/v2/tables/{tableid}/data"
    )

    # the whole dataset as JSON-stat2
    js2_data = response.json()

    # Get the dimensions of the dataset
    dimensions = {
        dim_name: list(dim_info["category"]["index"].keys())
        for dim_name, dim_info in js2_data["dimension"].items()
    }
    # Get the code to the dataframe
    dimension_combinations = list(itertools.product(*list(dimensions.values())))
    df = pd.DataFrame(dimension_combinations, columns=dimensions.keys())

    # Get the textlabels and add them next to codecolumn
    dimensions_labels = {
        dim_name: dim_info["category"]["label"]
        for dim_name, dim_info in js2_data["dimension"].items()
    }
    for i, (col, codelist) in enumerate(dimensions_labels.items()):
        label_colname = f"{col}_label"
        df.insert((i * 2 + 1), label_colname, df[col].map(codelist))

    # Add values to the dataframe
    df["Value"] = js2_data["value"]

    # Get metadata from dataset
    metadata = dict(
        table_id=js2_data["extension"]["px"]["tableid"],
        short_title=js2_data["extension"]["px"]["contents"],
        title=js2_data["label"],
        source=js2_data["source"],
        last_update=js2_data["updated"],
        # include footnote, needs post processing
        # note = js2_data['note']
    )

    return {"dataframe": df, "metadata": metadata}


if __name__ == "__main__":
    print(fetch_data_and_metadata("14706"))
