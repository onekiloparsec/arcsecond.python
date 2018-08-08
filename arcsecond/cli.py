import json
import pprint
import webbrowser

import click
import requests
from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers.data import JsonLexer

__version__ = '0.2.0'

pp = pprint.PrettyPrinter(indent=4, depth=5)


class State(object):
    def __init__(self):
        self.verbose = 0
        self.debug = False
        self.open = None


pass_state = click.make_pass_decorator(State, ensure=True)


class API(object):
    ENDPOINT_OBJECTS = ('/objects/', '/objects/')
    ENDPOINT_EXOPLANETS = ('/exoplanets/', '/objects/')

    ENPOINTS = [ENDPOINT_OBJECTS, ENDPOINT_EXOPLANETS]

    def __init__(self, state, endpoint):
        assert (endpoint in API.ENPOINTS)
        self.state = state
        self.endpoint = endpoint
        self.request_path = 'http://api.lvh.me:8000' if state.debug is True else 'https://api.arcsecond.io'
        self.open_path = 'http://localhost:8080' if state.debug is True else 'https://www.arcsecond.io'

    def url(self, name=''):
        path = self.request_path if self.state.open is False else self.open_path
        index = 0 if open is False else 1
        return "{}{}{}".format(path, self.endpoint[index], name)

    def run(self, name=''):
        url = self.url(name)

        if self.state.open:
            if self.state.verbose:
                click.echo('Opening URL in browser : ' + url)
            webbrowser.open(url)
        else:
            if self.state.verbose:
                click.echo('Requesting URL ' + url + ' ...')
            r = requests.get(url)
            if r.status_code == 200:
                json_str = json.dumps(r.json(), indent=4, sort_keys=True)
                print(highlight(json_str, JsonLexer(), TerminalFormatter()))
            else:
                print('error')


class AliasedGroup(click.Group):

    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx) if x[0] == cmd_name]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))


def verbose_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.verbose = value
        return value

    return click.option('-v', '--verbose', count=True,
                        expose_value=False,
                        help='Increases verbosity.',
                        callback=callback)(f)


def debug_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.debug = value
        return value

    return click.option('--debug/--no-debug',
                        expose_value=False,
                        help='Enables or disables debug mode.',
                        callback=callback)(f)


def open_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        state.open = value
        return value

    return click.option('-o', '--open',
                        is_flag=True,
                        expose_value=False,
                        help="Open the corresponding webpage in the default browser.",
                        callback=callback)(f)


def common_options(f):
    f = verbose_option(f)
    f = debug_option(f)
    f = open_option(f)
    return f


@click.group(cls=AliasedGroup, invoke_without_command=True)
@click.option('-v', '--version', is_flag=True)
@click.pass_context
def main(ctx, version=False):
    if ctx.invoked_subcommand is None and version:
        click.echo(__version__)


@main.command()
@click.argument('name', required=True, nargs=-1)
@common_options
@pass_state
def object(state, name):
    API(state, API.ENDPOINT_OBJECTS).run(name)


@main.command()
@click.argument('name', required=True, nargs=-1)
@common_options
@pass_state
def exoplanet(state, name):
    API(state, API.ENDPOINT_EXOPLANETS).run(name)
