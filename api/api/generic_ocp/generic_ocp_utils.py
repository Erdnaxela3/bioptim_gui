import json

import generic_ocp.generic_ocp_config as config


def update_generic_ocp_data(key: str, value) -> None:
    with open(config.DefaultGenericOCPConfig.datafile, "r") as f:
        data = json.load(f)
    data[key] = value
    with open(config.DefaultGenericOCPConfig.datafile, "w") as f:
        json.dump(data, f)


def read_generic_ocp_data(key: str = None):
    with open(config.DefaultGenericOCPConfig.datafile, "r") as f:
        data = json.load(f)
    return data if key is None else data[key]
