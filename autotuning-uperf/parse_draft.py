import types, datetime
import yaml
import os, pathlib

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
        results_list=[0]
    else:
        with result_file.open() as f:
            results_list = [int(x.strip()) for x in f.readline().split(",")]

    for i, val in enumerate(results_list):
        results = types.SimpleNamespace()
        results.nopm = val
        results.trial_num = trial_num
        entry_import_settings = {
            "system": study_name,
            "trial": trial_num,
            "benchmark": "hammerdb",
            #"argument": tuning_dict,
            #"id": results.Identifier,
            "@repeat": i,
        }
        print("entry_import_settings: {}".format(entry_import_settings))
        print("results: {}".format(str(results)))
        store.add_to_matrix(entry_import_settings, elt, results, _duplicated_entry)





def parse_data(results_dir):
    #store.register_custom_rewrite_settings(lambda x : x)

    for study in os.listdir(results_dir):
        # Going through each autotuning "study" which is a set of experiments with different tunables, converging on an optimum
        if os.path.isfile(study) or not study.startswith("study-"):
            continue
        
        print("Parsing study: {}".format(study))
        for trial in os.listdir(pathlib.Path(results_dir) / study):
            if os.path.isfile(trial) or not trial.startswith("trial-"):
                continue
            _parse_trial(str(pathlib.Path(results_dir) / study), trial)


parse_data("./results")