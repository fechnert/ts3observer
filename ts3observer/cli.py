'''
Created on Nov 9, 2014

@author: fechnert
'''

import sys, os
import time
import logging
import argparse
import traceback
from StringIO import StringIO
from ts3observer.observer import Supervisor


class CommandLineInterface(object):
    ''' Represents the commandline '''

    def __init__(self):
        ''' Initialize the Config '''
        self._parse_arguments()

    def _parse_arguments(self):
        ''' Parse runtime arguments '''
        parser = argparse.ArgumentParser()
        parser.add_argument('-v', '--verbose', action='store_true', help='Increase verbosity for debugging purpose')
        parser.add_argument('-g', '--graphical', action='store_true', help='Displays a \'gui\' inside the console')
        self.args = parser.parse_args()

    def _get_loglevel(self):
        ''' Get the loglevel out of the runtime arguments '''
        if self.args.verbose:
            return logging.DEBUG
        else:
            return logging.INFO

    def run(self):
        ''' Do some stuff '''
        if self.args.graphical:
            self.cli = GuiCli(self.args, self._get_loglevel())
        else:
            self.cli = StdCli(self.args, self._get_loglevel())
        self.cli.run()


class StdCli(object):
    ''' A normal, logging command line interface '''

    def __init__(self, args, level):
        ''' Set logging conf and get supervisor '''
        self.args = args
        logging.basicConfig(stream=sys.stdout,
                            level=level,
                            format='[%(asctime)s][%(levelname)s] %(message)s',
                            datefmt='%d.%m.%Y - %H:%M:%S')
        try: self.supervisor = Supervisor()
        except Exception as e:
            if self.args.verbose: print traceback.format_exc()
            else: logging.critical('{}: {}'.format(str(e.__class__.__name__), str(e))); quit(0)

    def run(self):
        ''' Run the ts3observer '''
        while True:
            start = time.time()
            self.execute()
            end = time.time()

            time_needed = end - start
            if time_needed >= self.supervisor.work_interval:
                logging.warn('More time needed than configured! ({} > {})'.format(time_needed, self.supervisor.work_interval))
            else:
                time.sleep(self.supervisor.work_interval - time_needed)

    def execute(self):
        ''' Execute the supervisor and catch exceptions '''
        try:
            self.supervisor.execute()
        except Exception as e:
            if self.args.verbose:
                logging.critical(traceback.format_exc())
            else:
                logging.critical('{}: {}'.format(str(e.__class__.__name__), str(e)))


class GuiCli(object):
    ''' A graphical command line interface (ascii art and stuff) '''

    def __init__(self, args, level):
        ''' Set logging conf and get supervisor '''
        self.args = args
        self.stream = StringIO()
        logging.basicConfig(stream=self.stream,
                            level=level,
                            format='[%(asctime)s][%(levelname)s] %(message)s',
                            datefmt='%H:%M:%S')
        self.supervisor = Supervisor()
        self.__set_stuff()

    def run(self):
        ''' Run the ts3observer '''
        while True:
            start = time.time()
            self.execute()
            end = time.time()

            run_duration = end - start
            self._print_screen(run_duration)
            if (self.supervisor.work_interval - run_duration) > 0:
                time.sleep(self.supervisor.work_interval - run_duration)

    def execute(self):
        ''' Execute the supervisor and catch exceptions '''
        try:
            self.supervisor.execute()
        except Exception as e:
            logging.critical('{}: {}'.format(str(e.__class__.__name__), str(e)))

    def _print_screen(self, run_duration):
        ''' print a gui like screen to display whats happening here '''
        os.system('clear')
        self.__draw_top_edge()
        self.__build_info(run_duration)
        self.__draw_lines()
        self.__draw_log()
        self.__draw_bottom_edge()

    def __set_stuff(self):
        ''' Set some stuff '''
        self.border_vchar = '\xe2\x80\x96'
        self.border_hchar = '='
        self.corner_char = 'O'
        self.col_width = 50
        self.info_size = 20
        self.log_size = 10
        self.log = []
        self.info = {}

    def __draw_lines(self):
        ''' Draw main info lines '''
        for i in range(self.info_size):
            self.__draw_line(
                self.__get_elem(self._get_clients(), -i - 1),
                self.__get_elem(self._get_queue(), -i - 1),
                self.__get_elem(self.info, i))

    def __draw_log(self):
        ''' Draw the log '''
        self.__draw_middle_edge()
        self.__get_log()
        for i in range(self.log_size):
            print('{0} {1:<{width}} {0}'.format(
                self.border_vchar, self.__get_elem(self.log, -self.log_size + i), width=self.col_width * 3))

    def __build_info(self, run_duration):
        ''' Build some kind of information '''
        self.info[1] = 'Time: {}'.format(time.time())
        self.info[3] = 'Clients : {}'.format(len(self.supervisor.clients))
        self.info[4] = 'In Queue: {}'.format(len(self.supervisor.queue))
        self.info[6] = 'Last run needed time:'
        self.info[7] = str(run_duration)
        self.info[9] = 'Sleeping now for:'
        self.info[10] = str(self.supervisor.work_interval - run_duration)

    def __get_elem(self, elem, index):
        ''' Get a element with index. catch exceptions ant return empty string '''
        try:
            stuff = elem[index]
        except Exception as e:
            if self.args.verbose:
                stuff = str(e)
            else:
                logging.debug(str(e))
                stuff = ''
        return stuff

    def __get_log(self):
        ''' get log stream and adds it to list '''
        for entry in self.stream.getvalue().split('\n'):
            if entry: self.log.append(entry)
        self.stream.truncate(0)

    def _get_clients(self):
        ''' Change the __repr__ of clients and returns them '''
        clients = []
        for clid, client in self.supervisor.clients.items():
            clients.append('{:<4} | {}'.format(clid, client))
        return clients

    def _get_queue(self):
        ''' Change the __repr__ of actions and returns them '''
        queue = []
        for name, action in self.supervisor.queue.items():
            queue.append('{0:<25} in {1:>7.2f} s'.format(': '.join(name.split('_')).replace('<', '').replace('>', ''),
                action.trigger_time - time.time()))
        return queue

    def __draw_line(self, col1, col2, col3):
        ''' Draw a line '''
        print('{0} {1:<{width}} {0} {2:<{width}} {0} {3:<{width}} {0}'.format(
            self.border_vchar, col1, col2, col3, width=self.col_width - 2))

    def __draw_top_edge(self):
        ''' Draw the top edge with headlines '''
        hl = {}
        hl['clients'] = '{0}[ Clients ]'.format(self.border_hchar * 2)
        hl['queue'] = '{0}[ Queue ]'.format(self.border_hchar * 2)
        hl['info'] = '{0}[ Info ]'.format(self.border_hchar * 2)

        print('{0}{clients:{1}<{width}}{0}{queue:{1}<{width}}{0}{info:{1}<{width}}{0}'.format(
            self.corner_char, self.border_hchar, width=self.col_width, **hl))

    def __draw_middle_edge(self):
        ''' Draw the middle edge '''
        print('{0}{log:{1}<{width}}{0}{1:{1}<{width}}{0}{1:{1}<{width}}{0}'.format(
            self.corner_char, self.border_hchar, width=self.col_width, log='{0}[ Log ]'.format(self.border_hchar)))

    def __draw_bottom_edge(self):
        ''' Draw horizontal edges '''
        print('{0}{1:{1}<{width}}{0}'.format(
            self.corner_char, self.border_hchar, width=(self.col_width * 3) + 2))
