from argparse import ArgumentParser, BooleanOptionalAction
from pathlib import Path

import openmc
import numpy as np
from matplotlib import pyplot as plt
from plotly.subplots import make_subplots
import configparser
import plotly.graph_objects as go


# Using this config parser to preserve case sensitivity
class MyConfigParser(configparser.ConfigParser):

    def __init__(self, *args, **kwargs):
        super(MyConfigParser, self).__init__(*args, **kwargs)
        self.optionxform = str


def gather_scaling_data(openmc_exe, input_path, max_threads, particles_per_thread):

    threads = np.array(range(0, max_threads, 5))
    inactive_particles = np.zeros(len(threads), dtype=int)
    active_particles = np.zeros(len(threads), dtype=int)
    inactive_time = np.zeros(len(threads), dtype=float)
    active_time = np.zeros(len(threads), dtype=float)

    for i, n_threads in enumerate(threads):
        n_threads = max(1, n_threads)

        openmc.reset_auto_ids()
        try:
            model = openmc.Model.from_model_xml(input_path + '/model.xml')
        except:
            paths = [input_path + '/' + p for p in ['geometry.xml', 'materials.xml', 'settings.xml', 'tallies.xml']]

            model = openmc.Model.from_xml(*paths)

        if model.settings.run_mode == 'eigenvalue':
            model.settings.batches = 10
            model.settings.inactive = 5
        if model.settings.run_mode == 'fixed source':
            model.settings.batches = 5

        threads[i] = n_threads
        for _ in range(n_runs):
            statepoint = model.run(openmc_exec=openmc_exe, threads=n_threads, particles=particles_per_thread*n_threads)

            with openmc.StatePoint(statepoint, autolink=False) as sp:
                inactive_particles[i] = sp.n_inactive * sp.n_particles
                active_particles[i] = sp.n_particles* (sp.n_batches - sp.n_inactive)
                inactive_time[i] += sp.runtime['inactive batches']
                active_time[i] += sp.runtime['active batches']

    inactive_time /= n_runs
    active_time /= n_runs

    inactive_rates = np.asarray(inactive_particles) / np.asarray(inactive_time)
    active_rates = np.asarray(active_particles) / np.asarray(active_time)

    return threads, inactive_rates, active_rates

def generate_model_figure(model_name, config):
    fig = make_subplots(rows=1, cols=2, subplot_titles=('Inactive Rate Scaling', 'Active Rate Scaling'))
    fig.update_xaxes(title_text='Threads', row=1, col=1)
    fig.update_yaxes(title_text='Particles per second', row=1, col=1)
    fig.update_xaxes(title_text='Threads', row=1, col=2)
    fig.update_yaxes(title_text='Particles per second', row=1, col=2)
    fig.update_layout(
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        xaxis2=dict(showgrid=True),
        yaxis2=dict(showgrid=True)
    )

    # ensure that the cache directory exists
    Path('./.cache').mkdir(exist_ok=True)

    input_path = config['models'][model_name]

    for j, (n, e) in enumerate(config['executables'].items()):

        data_file = './.cache/' / Path(f'{model_name}_{n}_scaling.csv')

        if config.getboolean('options', 'use_cache') and data_file.exists():
            print(f'Using cached data for {model_name} ({n})')
            data = np.loadtxt(data_file, delimiter=',')
            threads, inactive_rates, active_rates = data[:, 0], data[:, 1], data[:, 2]
        else:
            if n in config['max_threads']:
                max_threads = int(config['max_threads'][n])
            else:
                max_threads = MAX_THREADS
            print(f'Gathering scaling data for {model_name} ({n})')
            threads, inactive_rates, active_rates = gather_scaling_data(e, input_path, max_threads, particles_per_thread)

            data = np.column_stack((threads, inactive_rates, active_rates))
            np.savetxt(data_file, data, delimiter=',', header='Threads,Inactive rate,Active rate')

        if all(inactive_rates != np.nan):
            plt.figure()
            plt.title('Inactive Rate Scaling')
            plt.plot(threads, inactive_rates, label=f'Inactive rate ({model_name})')
            plt.xlabel('Threads')
            plt.ylabel('Particles per second')
            plt.legend()
            plt.grid()
            plt.savefig(f'{model_name}_{n}_inactive_rates.png')

        plt.figure()
        plt.title('Active Rate Scaling')
        plt.plot(threads, active_rates, label=f'Active rate ({model_name})')
        plt.xlabel('Threads')
        plt.ylabel('Particles per second')
        plt.legend()
        plt.grid()
        plt.savefig(f'{model_name}_{n}_active_rates.png')

        if all(inactive_rates != np.nan):
            fig.add_trace(
                go.Scatter(x=threads, y=inactive_rates, mode='lines+markers', name=n),
                row=1, col=1
            )

        fig.add_trace(
            go.Scatter(x=threads, y=active_rates, mode='lines+markers', name=n),
            row=1, col=2
        )

    return fig

MAX_THREADS = 90
n_runs = 1
particles_per_thread = 100


def model_figures(config_file='scaling_config.i'):
    config = MyConfigParser()
    config.optionxform = str
    config.read(config_file)

    figure_dict = {model_name : generate_model_figure(model_name, config) for model_name in config['models']}

    return figure_dict


def model_html(config_file='scaling_config.i'):
    figure_dict = model_figures(config_file)
    dashboard_files = {}
    for title, fig in figure_dict.items():
            filename = f"dashboards/{title.replace(' ', '_').lower()}.html"
            fig.write_html(filename, full_html=True, include_plotlyjs="cdn")
            dashboard_files[title] = filename
    return dashboard_files


def main():
    ap = ArgumentParser()

    ap.add_argument('--config', type=str, help='Path to configuration file', default='scaling_config.i')
    ap.add_argument('--use-cache', type=bool, help='Use cached data', action=BooleanOptionalAction, default=False)

    args = ap.parse_args()

    config = MyConfigParser()
    config.read(args.config)

    if args.use_cache:
        config.set('options', 'use_cache', 'True')

    print(f'Models: {config['models']}')
    print(f'OpenMC Executables: {config['executables']}')

    fig = make_subplots(rows=len(config['models']), cols=2, subplot_titles=('Inactive Rate Scaling', 'Active Rate Scaling'))
    fig.update_xaxes(title_text='Threads', row=1, col=1)
    fig.update_yaxes(title_text='Particles per second', row=1, col=1)
    fig.update_xaxes(title_text='Threads', row=1, col=2)
    fig.update_yaxes(title_text='Particles per second', row=1, col=2)
    fig.update_layout(
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        xaxis2=dict(showgrid=True),
        yaxis2=dict(showgrid=True)
    )

    figure_dict = model_figures(args.config)

    for i, (model_name, input_path) in enumerate(config['models'].items()):
        fig.update_yaxes(title_text=model_name, row=i+1, col=1)
        fig.update_yaxes(title_text=model_name, row=i+1, col=2)

    for model_name, fig in figure_dict.items():
        fig.write_html(f'{model_name}_dashboard.html')


if __name__ == '__main__':
    main()