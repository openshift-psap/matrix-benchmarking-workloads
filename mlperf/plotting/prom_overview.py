import plotly.graph_objs as go

import matrix_benchmarking.plotting.table_stats as table_stats
from matrix_benchmarking.common import Matrix

class Plot():
    def __init__(self, metric, y_title):
        self.name = f"Prom: {metric}"
        self.id_name = f"prom_overview_{metric}"
        self.metric = metric
        self.y_title = y_title

        table_stats.TableStats._register_stat(self)

    def do_hover(self, meta_value, variables, figure, data, click_info):
        return "nothing"

    def do_plot(self, ordered_vars, params, param_lists, variables, cfg):
        fig = go.Figure()

        plot_title = f"Prometheus: {self.metric} (overview)"
        y_max = 0
        x_start = None

        for entry in Matrix.all_records(params, param_lists):
            try: prom = entry.results.prom
            except AttributeError: continue

            for target, records in prom[self.metric].items():
                if x_start is None:
                    x_start = records[0][0]
                else:
                    x_start = min([x_start, records[0][0]])

        for entry in Matrix.all_records(params, param_lists):
            try: prom = entry.results.prom
            except AttributeError: continue

            for target, records in sorted(prom[self.metric].items()):
                name_key = "_".join(f"{k}={params[k]}" for k in ordered_vars)
                name = f"{name_key} | {target}"

                x = [(rec[0]-x_start)/60 for rec in records]
                y = [rec[1]*100 for rec in records]
                y_max = max([y_max]+y)

                trace = go.Scatter(x=x, y=y,
                                   name=name,
                                   hoverlabel= {'namelength' :-1},
                                   showlegend=True,
                                   mode='lines')
                fig.add_trace(trace)

        fig.update_layout(
            title=plot_title, title_x=0.5,
            yaxis=dict(title=self.y_title, range=[0, y_max*1.05]),
            xaxis=dict(title=f"Time (in minutes)"))

        return fig, ""
