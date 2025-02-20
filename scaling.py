from argparse import ArgumentParser, BooleanOptionalAction
from pathlib import Path
import json


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

def json_obj_hook(dct):
    for k, v in dct.items():
        if isinstance(v, list):
            dct[k] = np.asarray(v)
    return dct
class NumpyArrayEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def write_cache_file(model_name, executable_name, results):
    cache_file = Path('.cache')
    cache_file.mkdir(exist_ok=True)
    cache_file = cache_file / f'{model_name}_{executable_name}.json'
    with open(cache_file, 'w') as cache:
        json.dump(results, cache, indent=4, cls=NumpyArrayEncoder)

def check_cache(model_name, executable_name):
    cache_file = Path(f'.cache/{model_name}_{executable_name}.json')
    if cache_file.exists():
        with open(cache_file, 'r') as cache:
            return json.load(cache, object_hook=json_obj_hook)
    else:
        return None

def gather_scaling_data(model_name, openmc_exe, config):
    # check the cache for data if requrested
    if config.getboolean('options', 'use_cache', fallback=False):
        print(f'Attempting to use cached data for {model_name} ({openmc_exe})...', end=' ')
        results = check_cache(model_name, openmc_exe)
        if results is not None:
            print('Cached data found')
            return results
        print('No cached data found. Running simulations...')

    max_threads = config.getint('options', 'max_threads')
    if openmc_exe in config['exec_max_threads']:
        max_threads = min(config.getint('exec_max_threads', openmc_exe), max_threads)

    input_path = config['models'][model_name]

    # data storage
    threads = np.array(range(0, max_threads, 5))
    inactive_particles = np.zeros(len(threads), dtype=int)
    active_particles = np.zeros(len(threads), dtype=int)
    inactive_time = np.zeros(len(threads), dtype=float)
    active_time = np.zeros(len(threads), dtype=float)


    executable = config['executables'][openmc_exe]

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

        # add flux tally to model based on fine energy group structure
        tally = openmc.Tally()
        tally.scores = ['flux']
        e_filter = openmc.EnergyFilter.from_group_structure('CCFE-709')
        tally.filters = [e_filter]

        model.tallies.append(tally)

        results = {}

        particles_per_thread = config.getint('options', 'particles_per_thread')
        output = config.getboolean('options', 'output')

        print(f'Running {openmc_exe} with {n_threads} threads')
        threads[i] = n_threads
        n_runs = config.getint('options', 'n_repeats')
        for _ in range(n_runs):
            statepoint = model.run(openmc_exec=executable, threads=n_threads, particles=particles_per_thread*n_threads, output=output)

            with openmc.StatePoint(statepoint, autolink=False) as sp:
                inactive_particles[i] = sp.n_inactive * sp.n_particles
                active_particles[i] = sp.n_particles* (sp.n_batches - sp.n_inactive)
                inactive_time[i] += sp.runtime['inactive batches']
                active_time[i] += sp.runtime['active batches']

        # after the last run, get some data from the final statepoint.
        # it will be run with the most particles and results should
        # have the lowest variance
        with openmc.StatePoint(statepoint, autolink=False) as sp:
                if sp.run_mode == 'eigenvalue':
                    eigenvalue = sp.keff.nominal_value
                else:
                    eigenvalue = None

                # extract flux results from the statepoint file
                sp_tally = sp.tallies[tally.id]
                flux_results = sp_tally.get_reshaped_data().squeeze()
                energy_divs = e_filter.values

    inactive_time /= n_runs
    active_time /= n_runs

    inactive_rates = np.asarray(inactive_particles) / np.asarray(inactive_time)
    active_rates = np.asarray(active_particles) / np.asarray(active_time)

    results['inactive_rates'] = inactive_rates
    results['active_rates'] = active_rates
    results['threads'] = threads
    results['eigenvalue'] = eigenvalue
    results['flux_values'] = flux_results
    results['energy_divs'] = energy_divs

    write_cache_file(model_name, openmc_exe, results)

    return results


def generate_model_figure(model_name, results):
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=('Flux vs Energy', 'Inactive Rate Scaling', 'Active Rate Scaling'),
        specs=[[{"colspan": 2}, None], [{}, {}], [{"colspan": 2, "type": "table"}, None]]
    )
    fig.update_xaxes(title_text='Energy (eV)', row=1, col=1)
    fig.update_yaxes(title_text='Flux', row=1, col=1)
    fig.update_xaxes(title_text='Threads', row=2, col=1)
    fig.update_yaxes(title_text='Particles per second', row=2, col=1)
    fig.update_xaxes(title_text='Threads', row=2, col=2)
    fig.update_yaxes(title_text='Particles per second', row=2, col=2)
    fig.update_layout(
        xaxis=dict(showgrid=True, type='log'),
        yaxis=dict(showgrid=True, type='log'),
        xaxis2=dict(showgrid=True),
        yaxis2=dict(showgrid=True),
        xaxis3=dict(showgrid=True),
        yaxis3=dict(showgrid=True)
    )

    eigenvalues = []
    for n, r in results.items():
        threads, inactive_rates, active_rates = r['threads'], r['inactive_rates'], r['active_rates']
        flux_values, energy_divs = r['flux_values'], r['energy_divs']
        eigenvalue = f'{r["eigenvalue"]:0.7f}' if r['eigenvalue'] is not None else 'N/A'
        eigenvalues.append([n, eigenvalue])

        fig.add_trace(
            go.Scatter(x=energy_divs, y=flux_values, mode='lines+markers', name=f'{n} Flux', line_shape='hv', legendgroup='flux', legendgrouptitle_text="Flux", showlegend=True),
            row=1, col=1
        )

        if all(inactive_rates != np.nan):
            fig.add_trace(
                go.Scatter(x=threads, y=inactive_rates, mode='lines+markers', name=n, legendgroup='inactive', legendgrouptitle_text="Inatcive Rates", showlegend=True),
                row=2, col=1
            )

        fig.add_trace(
            go.Scatter(x=threads, y=active_rates, mode='lines+markers', name=n, legendgroup='active', legendgrouptitle_text="Active Rates", showlegend=True),
            row=2, col=2
        )


    fig.add_trace(
        go.Table(
            header=dict(values=['Executable', 'Eigenvalue']),
            cells=dict(values=list(zip(*eigenvalues)))
        ),
        row=3, col=1
    )

    fig.update_layout(
        legend=dict(
            x=1,
            y=1,
            tracegroupgap=50,
        ),
    )

    return fig

def model_results(model_name, config):
    execuable_results = {}
    for executable_name in config['executables']:
        execuable_results[executable_name] = gather_scaling_data(model_name, executable_name, config)
    return execuable_results


def get_all_results(config_file='scaling_config.i'):
    if not isinstance(config_file, MyConfigParser):
        config = MyConfigParser()
        config.optionxform = str
        config.read(config_file)
    else:
        config = config_file

    all_results = {}
    for model_name in config['models']:
        all_results[model_name] = model_results(model_name, config)
    return all_results


def model_figures(config, all_results=None):
    if all_results is None:
        all_results = get_all_results(config)
    figure_dict = {}
    for model_name in config['models']:
        figure_dict[model_name] = generate_model_figure(model_name, all_results[model_name])
    return figure_dict


def get_config(config_file='scaling_config.i'):
    config = MyConfigParser()
    config.read(config_file)
    return config

def model_flux_figure(model_name, config, all_results):
    fig = make_subplots(rows=1, cols=1, subplot_titles=(f'{model_name} Flux'))

    fig.update_xaxes(title_text='Energy (eV)', row=1, col=1)
    fig.update_yaxes(title_text='Flux', row=1, col=1)
    fig.update_layout(
        xaxis=dict(showgrid=True, type='log'),
        yaxis=dict(showgrid=True, type='log')
    )

    results = all_results[model_name]
    for executable_name, exec_results in results.items():
        energy_divs = exec_results['energy_divs']
        flux_values = exec_results['flux_values']

        fig.add_trace(
            go.Scatter(x=energy_divs, y=flux_values, mode='lines+markers', name=executable_name, line_shape='hv'),
            row=1, col=1
        )

    return fig

def flux_figures(config, all_results=None):
    if all_results is None:
        all_results = get_all_results(config)
    figure_dict = {}
    for model_name in config['models']:
        figure_dict[model_name] = model_flux_figure(model_name, config, all_results)
    return figure_dict

def model_html(config_file='scaling_config.i'):
    config = get_config(config_file)
    all_results = get_all_results(config)
    figure_dict = model_figures(config, all_results)
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

    config = get_config(args.config)
    results = get_all_results(config)
    figure_dict = model_figures(config, results)

    for i, (model_name, input_path) in enumerate(config['models'].items()):
        fig.update_yaxes(title_text=model_name, row=i+1, col=1)
        fig.update_yaxes(title_text=model_name, row=i+1, col=2)

    for model_name, fig in figure_dict.items():
        fig.write_html(f'{model_name}_dashboard.html')


if __name__ == '__main__':
    main()