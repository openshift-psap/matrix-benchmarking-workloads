import types

import matrix_benchmarking.store as store
import matrix_benchmarking.store.simple as store_simple

def _rewrite_settings(params_dict):
    return params_dict


def parse_benchmark_results(dirname, import_settings):
    results = types.SimpleNamespace()

    with open(f"{dirname}/benchmarking_run_ssd_bench_duration.log") as f:
        content = f.read()
        results.duration = int(content.split()[0])

    with open(f"{dirname}/benchmarking_run_ssd_sample_rate.log") as f:
        content = f.read()
        results.rate = float(content.split()[0])

    return results


def _parse_results(fn_add_to_matrix, dirname, import_settings):

    if import_settings["benchmark"] != "benchmark":
        return

    results = parse_benchmark_results(dirname, import_settings)
    if results is None:
        return

    fn_add_to_matrix(results)


def parse_data():
    # delegate the parsing to the simple_store
    store.register_custom_rewrite_settings(_rewrite_settings)
    store_simple.register_custom_parse_results(_parse_results)

    return store_simple.parse_data()
