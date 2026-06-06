import itertools
from typing import Any

import pandas as pd
import requests


def fetch_data_and_metadata(table_id: str) -> dict[str, Any]:
    """
    Fetch one full SSB table as JSON-stat2 and convert it to a pandas DataFrame.

    Returns:
        {
            "dataframe": pd.DataFrame,
            "metadata": dict
        }

    Important:
        JSON-stat stores values as a flat list.
        The dimension combinations are generated in the same row-major order
        so that the values line up correctly with the rows.
    """

    url = f"https://data.ssb.no/api/pxwebapi/v2/tables/{table_id}/data"

    response = requests.get(url)
    response.raise_for_status()

    js2_data = response.json()

    dimension_info = js2_data["dimension"]

    dimension_names = []
    dimension_code_lists = []
    dimension_label_maps = {}

    for dimension_name, info in dimension_info.items():
        category = info["category"]

        code_to_position = category["index"]
        code_to_label = category["label"]

        codes = list(code_to_position.keys())

        dimension_names.append(dimension_name)
        dimension_code_lists.append(codes)
        dimension_label_maps[dimension_name] = code_to_label

    dimension_combinations = list(itertools.product(*dimension_code_lists))

    df = pd.DataFrame(
        dimension_combinations,
        columns=dimension_names,
    )

    for dimension_name in dimension_names:
        label_column_name = f"{dimension_name}_label"
        label_map = dimension_label_maps[dimension_name]

        df[label_column_name] = df[dimension_name].map(label_map)

    df["Value"] = js2_data["value"]

    metadata = {
        "table_id": js2_data["extension"]["px"]["tableid"],
        "short_title": js2_data["extension"]["px"]["contents"],
        "title": js2_data["label"],
        "source": js2_data["source"],
        "last_update": js2_data["updated"],
        "note": js2_data.get("note"),
    }

    return {
        "dataframe": df,
        "metadata": metadata,
    }
