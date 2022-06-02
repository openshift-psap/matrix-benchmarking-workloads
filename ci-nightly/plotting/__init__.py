from collections import defaultdict
from datetime import datetime
import statistics as stats

import plotly.graph_objs as go

import matrix_benchmarking.plotting.table_stats as table_stats
from matrix_benchmarking.common import Matrix

def register():
    table_stats.TableStats.ValueDev(
        "rate", "Training rate",
        lambda entry: entry.results.rate,
        ".2f", "samples/sec",
        higher_better=False,
    )

    table_stats.TableStats.ValueDev(
        "duration", "Training duration",
        lambda entry: entry.results.duration,
        ".0f", "min",
        higher_better=False,
    )

    NightlyPlot(key="rate")
    NightlyPlot(key="duration")


class NightlyPlot():
    def __init__(self, key):
        self.key = key
        self.name = "Nightly " + self.key.replace("_", " ").title()

        self.id_name = self.name.lower().replace(" ", "_")

        table_stats.TableStats._register_stat(self)
        Matrix.settings["stats"].add(self.name)

    def do_hover(self, meta_value, variables, figure, data, click_info):
        # would be nice to be able to compute a link to the test results here
        return "nothing"

    def do_plot(self, ordered_vars, params, param_lists, variables, cfg):
        fig = go.Figure()
        plot_title = self.name

        plot_values = defaultdict(list)
        entries = []

        dates_values = defaultdict(list)
        dates = defaultdict(list)
        names = set()
        y_max = 0
        for entry in Matrix.all_records(params, param_lists):
            def add_plot(an_entry):
                nonlocal y_max

                date_str = an_entry.import_settings["@finish-date"]
                date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')

                try:
                    value = an_entry.results.__dict__[self.key]
                except KeyError: return

                name = ",".join([f"{var}={params[var]}" for var in ordered_vars if var != "benchmark"])
                y_max = max([y_max, value])
                dates_values[name].append([date, value])
                names.add(name)

            if entry.is_gathered:
                for single_entry in entry.results:
                    add_plot(single_entry)
            else:
                add_plot(entry)

        for name in sorted(names):
            current_dates_values = dates_values[name]
            current_dates_values = sorted(current_dates_values)
            dates = [dt_sp[0] for dt_sp in current_dates_values]
            values = [dt_sp[1] for dt_sp in current_dates_values]

            fig.add_trace(
                go.Scatter(x=dates, y=values,
                           name="Nighly processing rate",
                           hoverlabel= {'namelength' :-1},
                           showlegend=True,
                           mode='markers+lines')
            )

            mean = stats.mean(values)
            fig.add_trace(
                go.Scatter(x=dates, y=[mean*0.95 for _ in values],
                           name="Average * 95%",
                           hoverlabel= {'namelength' :-1},
                           showlegend=True,
                           line_width=2,
                           mode='lines')
            )
            fig.add_trace(
                go.Scatter(x=dates, y=[mean*1.05 for _ in values],
                           name="Average * 105%",
                           hoverlabel= {'namelength' :-1},
                           showlegend=True,
                           line_width=2,
                           mode='lines')
            )


        fig.update_layout(
            yaxis=dict(title="",
                       range=[0, y_max*1.05],
                       ),
            title="Processing rate (in img/sec, higher is better)", title_x=0.5)
        return fig, ""
