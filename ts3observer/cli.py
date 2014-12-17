'''
Created on Nov 9, 2014

@author: fechnert
'''

import sys, os
import time
import logging
import argparse
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
            self.cli = GuiCli(self._get_loglevel())
        else:
            self.cli = StdCli(self._get_loglevel())
        self.cli.run()


class StdCli(object):
    ''' A normal, logging command line interface '''

    def __init__(self, level):
        ''' Set logging conf and get supervisor '''
        logging.basicConfig(stream=sys.stdout,
                            level=level,
                            format='[%(asctime)s][%(levelname)s] %(message)s',
                            datefmt='')
        self.supervisor = Supervisor()

    def run(self):
        ''' Run the ts3observer '''
        while True:
            start = time.time()
            self.supervisor.execute()
            end = time.time()

            time_needed = end - start
            if time_needed >= self.supervisor.work_interval:
                logging.warn('More time needed than configured! ({} > {})'.format(time_needed, self.supervisor.work_interval))
            else:
                # logging.info('Sleeping {} seconds ...'.format(self.supervisor.work_interval - time_needed))
                time.sleep(self.supervisor.work_interval - time_needed)


class GuiCli(object):
    ''' A graphical command line interface (ascii art and stuff) '''

    def __init__(self, level):
        ''' Set logging conf and get supervisor '''
        self.stream = StringIO()
        logging.basicConfig(stream=self.stream,
                            level=level,
                            format='[%(levelname)s] %(message)s')
        self.supervisor = Supervisor()

    def run(self):
        ''' Run the ts3observer '''
        while True:
            start = time.time()
            self.supervisor.execute()
            end = time.time()
            run_duration = end - start
            self._print_screen(run_duration)
            time.sleep(self.supervisor.work_interval - run_duration)

    def _print_screen(self, run_duration):
        ''' print a gui like screen to display whats happening here '''
        os.system('clear')
        self.__set_stuff()
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
                self.__get_elem(self.supervisor.clients.items(), -i - 1),
                self.__get_elem(self.supervisor.queue.items(), -i - 1),
                self.__get_elem(self.info, i))

    def __draw_log(self):
        ''' Draw the log '''
        self.__draw_middle_edge()
        self.__get_log()
        for i in range(self.log_size):
            print('{0} {1:<{width}} {0}'.format(
                self.border_vchar, self.__get_elem(self.log, -self.log_size - 1 + i), width=self.col_width * 3))

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
        except (IndexError, KeyError):
            stuff = ''
        return stuff

    def __draw_line(self, col1, col2, col3):
        ''' Draw a line '''
        print('{0} {1:<{width}} {0} {2:<{width}} {0} {3:<{width}} {0}'.format(
            self.border_vchar, col1, col2, col3, width=self.col_width - 2))

    def __get_log(self):
        ''' get log stream and adds it to list '''
        map(self.log.append, self.stream.getvalue().split('\n'))

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






























