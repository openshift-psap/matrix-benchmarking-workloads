import types, datetime
import yaml
import logging
import io

import matrix_benchmarking.store as store
import matrix_benchmarking.store.simple as store_simple
import matrix_benchmarking.store.prom_db as store_prom_db
import matrix_benchmarking.parsing.prom as parsing_prom

def _rewrite_settings(settings_dict):
    # no rewriting to do at the moment
    settings_dict.pop("expe")
    if "num_pods" not in settings_dict:
        settings_dict["num_pods"] = "1"
    if "num_gpu_per_per_pod" not in settings_dict:
        settings_dict["num_gpu_per_per_pod"] = "1"

    #del settings_dict["batch_size"]
    if settings_dict["mpi_mode"] == "reference":
        return None
    settings_dict.pop("num_pods")
    return settings_dict

INTERESTING_METRICS = [
    "DCGM_FI_DEV_POWER_USAGE",
    "DCGM_FI_DEV_FB_USED",
    "DCGM_FI_DEV_GPU_UTIL",
    "container_network_transmit_bytes_total",
    "pod:container_cpu_usage:sum",
]

def _parse_results(fn_add_to_matrix, dirname, import_settings):
    results = types.SimpleNamespace()
    if 'batch_size_per_gpu' in import_settings:
        store.simple.invalid_directory(dirname, import_settings, "invalid BS configuration")
        return

    #results.gpu_power_usage = sum(parsing_prom.mean(results.metrics["DCGM_FI_DEV_POWER_USAGE"], "run-bert"))
    #results.gpu_compute_usage = sum(parsing_prom.mean(results.metrics["DCGM_FI_DEV_GPU_UTIL"], "run-bert"))
    #results.gpu_memory_usage = sum(parsing_prom.mean(results.metrics["DCGM_FI_DEV_FB_USED"], "run-bert"))
    #results.cpu_usage = sum(parsing_prom.mean(results.metrics["pod:container_cpu_usage:sum"], "run-bert"))
    #results.network_usage = sum(parsing_prom.last(results.metrics["container_network_transmit_bytes_total"], "run-bert"))

    with open(list(dirname.glob("pod.*-launcher*.log"))[0]) as f:
        for line in f.readlines():
            if "Resource exhausted" in line:
                store.simple.invalid_directory(dirname, import_settings, "OOM detected")
                return

            prefix, delim, msg = line.strip().partition("] ")

            if "Total Training Time" in msg:
                # Total Training Time = 4974.69 for Sentences = 177276
                results.training_time = float(msg.split()[4])
                results.sentences = int(msg.split()[-1])
                results.training_time_units = "seconds"

            if "Throughput Average" in msg:
                # Throughput Average (sentences/sec) with overhead = 35.99
                # or
                # Throughput Average (sentences/sec) = 38.56

                throughput = msg.split()[-1]

                if "with overhead" in msg:
                    results.throughput_with_overhead = float(throughput)
                else:
                    results.throughput = float(throughput)

                results.throughput_units = msg.split()[2].strip("()")

    if "throughput" not  in results.__dict__:
        store.simple.invalid_directory(dirname, import_settings, "no result generated")
        return

    fn_add_to_matrix(results)
    if import_settings["mpi_mode"] == "all_in_one_pod" and import_settings["num_gpu"] == "1":
        for num_pods in 2, 4, 8:
            settings = import_settings.copy()
            settings["mpi_mode"] = "test-gpu-per-pod"
            settings["num_gpu"] = "1"
            settings["num_gpu_per_per_pod"] = str(int(16/num_pods))
            settings["num_pods"] = "1"
            fn_add_to_matrix(results, settings)
    pass

# https://github.com/NVIDIA/DeepLearningExamples/tree/master/TensorFlow2/LanguageModeling/BERT#fine-tuning-training-performance-for-squad-v11-on-nvidia-dgx-1-v100-8x-v100-16gb
REFERENCE_VALUES = [
    dict(num_gpu="1", batch_size="6", precision="fp16", throughput=39.10),
    dict(num_gpu="4", batch_size="6", precision="fp16", throughput=128.48),
    dict(num_gpu="8", batch_size="6", precision="fp16", throughput=255.36),

    dict(num_gpu="1", batch_size="3", precision="fp32", throughput=9.85),
    dict(num_gpu="4", batch_size="3", precision="fp32", throughput=36.52),
    dict(num_gpu="8", batch_size="3", precision="fp32", throughput=73.03),
]

def parse_data():
    # delegate the parsing to the simple_store
    store.register_custom_rewrite_settings(_rewrite_settings)
    store_simple.register_custom_parse_results(_parse_results)

    for _ref_value in REFERENCE_VALUES:
        ref_values = _ref_value.copy()

        results = types.SimpleNamespace()
        results.training_time = None
        results.sentences = None
        results.throughput_with_overhead = None
        results.throughput = ref_values["throughput"]

        del ref_values["throughput"]
        ref_values["mpi_mode"] = "reference"
        ref_values["expe"] = "run-parallel"
        ref_values["run"] = "1"

        store.add_to_matrix(ref_values,
                            "<website>", results,
                            None)

    return store_simple.parse_data()
