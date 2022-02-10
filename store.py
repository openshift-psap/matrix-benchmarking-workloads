import types, datetime
import yaml

import store
import store.simple
from store.simple import *

def sample_rewrite_settings(params_dict):
    # add a @ on top of parameter name 'run'
    # to treat it as multiple identical executions

    params_dict["@run"] = params_dict["run"]
    del params_dict["run"]

    # if parameter 'run' was missing, set '0' as default value
    if params_dict["@run"] == "":
        params_dict["@run"] = "0"

    # overwrite 'operation' parameter
    mode = params_dict.pop("mode")
    op = params_dict.pop("operation")
    params_dict["operation"] = f"{mode}-{op}"

    # remove the 'expe' setting
    params_dict.pop("expe")

    return params_dict

def __parse_date(dirname, settings):
    results = types.SimpleNamespace()

    with open(f"{dirname}/date") as f:
        results.date_ts = int(f.readlines()[0])

    return results

def __parse_procs(dirname, settings):
    results = types.SimpleNamespace()

    with open(f"{dirname}/procs") as f:
        results.procs = int(f.readlines()[0])

    return results

def __parse_memfree(dirname, settings):
    results = types.SimpleNamespace()

    with open(f"{dirname}/memfree") as f:
        results.memfree = int(f.readlines()[0]) * 1000 # unit if kB

    return results

def sample_parse_results(dirname, settings):
    mode = settings.get("mode")
    if not mode:
        print(f"ERROR: failed to parse '{dirname}', 'mode' setting not defined.")
        return

    mode_fct = {
        "date":  __parse_date,
        "procs": __parse_procs,
        "memfree":  __parse_memfree,
    }

    fct = mode_fct.get(mode)
    if not fct:
        print(f"ERROR: failed to parse '{dirname}', mode={mode} not recognized.")
        return

    return [[{}, fct(dirname, settings)]]

store.custom_rewrite_settings = sample_rewrite_settings
store.simple.custom_parse_results = sample_parse_results
