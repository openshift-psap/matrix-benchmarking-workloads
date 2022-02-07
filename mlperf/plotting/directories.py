from dash import html

from matrix_benchmarking.common import Matrix
import matrix_benchmarking.plotting.table_stats as table_stats

class Directories():
    def __init__(self, mig_type=None, speed=False):
        self.name = "Directories"

        self.id_name = self.name.lower()
        self.no_graph = True

        table_stats.TableStats._register_stat(self)

    def do_hover(self, meta_value, variables, figure, data, click_info):
        return "nothing"

    def do_plot(self, ordered_vars, settings, param_lists, variables, cfg):
        elts = [html.P(html.B(", ".join([f"{k}={v}" for k, v in settings.items() if v != "---"])))]

        elements = {}
        for entry in Matrix.all_records(settings, param_lists):
            gpu_name = entry.settings.gpu_type
            li_elts = []

            key = " " + ", ".join([f"{k}={entry.settings.__dict__[k]}" for k in reversed(ordered_vars)])

            if entry.is_gathered:
                for k, v in entry.gathered_keys.items():
                    key += f", {k}={{{' '.join(v)}}}"

            settings = html.B(key)
            li_elts.append(html.A("link", href=f"file://{entry.location}"))
            li_elts.append(html.Span(settings))

            elements[key] = html.Li(li_elts)

        for k in sorted(elements):
            elts.append(elements[k])

        return None, html.Ul(elts)
