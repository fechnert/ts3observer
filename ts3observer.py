#!/usr/bin/env python

import os, argparse, logging
from ts3observer.cli import CommandLineInterface as Cli
from ts3observer.gui import GraphicalUserInterface as Gui
from ts3observer.utils import path
from ts3observer.exc import CriticalException, ShutDownException, print_traceback, print_buginfo


class Dispatcher(object):
    ''' Dispatch the task to the right module '''

    def __init__(self):
        self._parse_arguments()

    def _parse_arguments(self):
        ''' Parse the arguments from commandline '''
        parser = argparse.ArgumentParser()
        sub_parser = parser.add_subparsers(dest='task')

        parser.add_argument('-v', '--verbose', action='store_true', help='Increase verbosity for debugging purpose')
        parser.add_argument('-q', '--quiet', action='store_true', help='Only show messaged if there is an critical Exception')
        parser.add_argument('-g', '--graphical', action='store_true', help='Run the ts3observer as Gui')
        parser.add_argument('-d', '--dev', action='store_true', help='Run in developer modus')

        run_parser = sub_parser.add_parser('run', help='Run the ts3observer')
        version_parser = sub_parser.add_parser('version', help='Shows the ts3observer version')

        ts3o.args = parser.parse_args()

    def dispatch(self):
        ''' Dispatch the task to the right module '''
        if ts3o.args.graphical:
            getattr(Gui(), ts3o.args.task)()
        else:
            getattr(Cli(), ts3o.args.task)()


class Ts3o(object):
    ''' Define a holder class '''
    pass

def _setup():
    ''' Define some globals for ts3observer '''
    __builtins__.ts3o = Ts3o()
    ts3o.base_path = os.path.abspath(os.path.dirname(__file__))

def _run():
    try:
        _setup()
        Dispatcher().dispatch()

    except ShutDownException as e:
        logging.info('Good Bye!')

    except CriticalException as e:
        if ts3o.args.verbose: print_traceback()
        logging.critical('{}: {}'.format(e.__class__.__name__, str(e)))

    except Exception as e:
        print_traceback()
        logging.critical('{}: {}'.format(e.__class__.__name__, str(e)))
        print_buginfo()

if __name__ == '__main__':
    _run()
else:
    raise Exception('Please, run this script directly!')
