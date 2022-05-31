import types, datetime
import re
import yaml
import os, pathlib

import matrix_benchmarking.store as store
import matrix_benchmarking.common as common
import matrix_benchmarking.cli_args as cli_args

def _duplicated_entry(import_key, old_location, new_location):
    pass

def _parse_trial(dir_name, trial_name):
    study_name = dir_name.split("/")[-1]
    trial_num = trial_name.split("-")[1]
    print("Parsing trial: {} in study: {}".format(trial_num, study_name))

    #TODO fil tuning_dict with all tuning params
    result_file=pathlib.Path(dir_name) / trial_name / "result.csv"

    # In each trial, we repeat the run n times, and put the results of all runs in a result.csv. Each run will be registered to matrix benchmarking separately:
    results_list=[]
    # Some results may be pruned or incomplete. For now call result 0
    if not result_file.exists():
        results_list=[None]
    else:
        with result_file.open() as f:
            results_list = [float(x.strip()) for x in f.readline().split(",")]

    tuned_yaml=pathlib.Path(dir_name) / trial_name / "tuned.yaml"
    tuned_dict={}
    # Some results may be pruned or incomplete. For now call result 0
    if not tuned_yaml.exists():
        tuned_yaml=[None]
    else:
        sysctl_regex=re.compile(".+=[0-9]+")
        with tuned_yaml.open() as f:
            for line in f:
                if(re.match(sysctl_regex, line.strip())):
                    tuned_setting = line.strip().split('=')
                    tuned_dict[tuned_setting[0].replace(".", "-")] = int(tuned_setting[1])

    for i, val in enumerate(results_list):
        results = types.SimpleNamespace()
        results.latency = val
        results.trial = int(trial_num)

        results.__dict__["trial_num"] = trial_num
        #results.__dict__.update(tuned_dict)
        entry_import_settings = {
            "study": study_name,
            #"trial": int(trial_num),
            "benchmark": "uperf",
            #"argument": tuning_dict,
            #"id": results.Identifier,
            "@repeat": i,
        }
        entry_import_settings.update(tuned_dict)
        print("entry_import_settings: {}".format(entry_import_settings))
        print("results: {}".format(str(results)))
        store.add_to_matrix(entry_import_settings, study_name, results, _duplicated_entry)


def parse_data():
    store.register_custom_rewrite_settings(lambda x : x)

    results_dir = pathlib.Path(".") / cli_args.kwargs["results_dirname"]

    for study in os.listdir(results_dir):
        # Going through each autotuning "study" which is a set of experiments with different tunables, converging on an optimum
        if os.path.isfile(study) or not study.startswith("study-"):
            continue

        print("Parsing study: {}".format(study))
        for trial in os.listdir(pathlib.Path(results_dir) / study):
            if os.path.isfile(trial) or not trial.startswith("trial-"):
                continue
            _parse_trial(str(pathlib.Path(results_dir) / study), trial)
