'''
Created on Jan 26, 2015

@author: fechnert
'''

import logging
import time
import telnetlib
from models import Client
from utils import TelnetUtils, Escaper, PropertyMapper


class TelnetInterface(object):
    ''' Provide a interface for the telnet connection '''

    def __init__(self):
        self.tn = None

    def connect(self, host, port):
        ''' Connect with the teamspeak server instance '''
        logging.info('Connecting to \'{}:{}\' ...'.format(host, port))
        self.tn = telnetlib.Telnet(host, port)
        time.sleep(1)  # Ugly, know ... but telnet is slow
        self.tn.read_very_eager()  # clear cache

    def login(self, user, password):
        ''' Log into the teamspeak server instance as given user with password '''
        logging.info('Logging in as \'{}\' ...'.format(user))
        self._query('login {} {}'.format(user, password))

    def choose_vserv(self, servid):
        ''' Use a specific virtual server '''
        logging.info('Choosing virtual server \'{}\' ...'.format(servid))
        self._query('use {}'.format(servid))

    def change_displayname(self, name):
        ''' Change the nickname of the bot '''
        logging.info('Changing displayname to \'{}\' ...'.format(name))
        uname = Escaper.encode(name)
        self._query('clientupdate client_nickname={}'.format(uname))

    def get_clientlist(self):
        ''' Get the list of clients '''
        client_info = self._query('clientlist').split('|')

        client_info_list = []
        for string in client_info:
            client_info_list.append(PropertyMapper.string_to_dict(string))
        return client_info_list

    def get_client(self, clid):
        ''' Get a client by clid '''
        client_str = self._query('clientinfo clid={}'.format(clid))
        client_dict = PropertyMapper.string_to_dict(client_str)
        return Client(clid, **client_dict)

    @Escaper.encode_attr('reason')
    def clientaction_kick(self, client_obj, featurename, reasonid, reason='ByeBye', **kwargs):
        ''' Kick a client '''
        self._query('clientkick reasonid={} reasonmsg={} clid={}'.format(
            reasonid, reason, client_obj.clid))
        logging.info('{} kicked {}'.format(
            featurename, client_obj.decoded_nickname))

    def clientaction_move(self, client_obj, featurename, to, **kwargs):
        ''' Move a client :to: a channel '''
        if int(client_obj.cid) != to:
            ocid = client_obj.cid
            self._query('clientmove cid={} clid={}'.format(
                to, client_obj.clid))
            logging.info('{} moved {} (from cid {} to {})'.format(
                featurename, client_obj.decoded_nickname, ocid, to))
            client_obj.cid = to

    @Escaper.encode_attr('reason')
    def clientaction_ban(self, client_obj, featurename, time=0, reason='Kicked', **kwargs):
        ''' Ban a client for :sfor: seconds '''
        if time:
            self._query('banclient clid={} banreason={} time={}'.format(
                client_obj.clid, reason, time))
        else:
            self._query('banclient clid={} banreason={}'.format(
                client_obj.clid, reason))
        logging.info('{} banned {} for {} seconds (0 = permanent)'.format(
            featurename, client_obj.decoded_nickname, time))

    def clientaction_show(self, client_obj, featurename, **kwargs):
        ''' Only shows the clientname (for debugging purpose) '''
        logging.info('{}: {}'.format(featurename, client_obj.decoded_nickname))

    @Escaper.encode_attr('message')
    def clientaction_poke(self, client_obj, featurename, message, **kwargs):
        ''' Poke a client with given message '''
        self._query('clientpoke clid={} msg={}'.format(
            client_obj.clid, message))

    @Escaper.encode_attr('message')
    def clientaction_chat(self, client_obj, featurename, targetmode, target, message, **kwargs):
        ''' Send a text message to specific target, depending on targetmode '''
        self._query('sendtextmessage targetmode={} target={} msg={}'.format(
            targetmode, target, message))

    @Escaper.encode_attr('message')
    def clientaction_notify(self, client_obj, featurename, message, **kwargs):
        ''' Send a message to this client '''
        self._query('sendtextmessage targetmode=1 target={} msg={}'.format(
            client_obj.clid, message))

    def clientaction_group_set(self, client_obj, featurename, sgid, **kwargs):
        ''' Sets servergroups for a client '''
        for gid in client_obj.client_servergroups:
            self._query('servergroupdelclient sgid={} cldbid={}'.format(
                gid, client_obj.client_database_id))
        if type(sgid) == int:
            self._query('servergroupaddclient sgid={} cldbid={}'.format(
                sgid, client_obj.client_database_id))
        if type(sgid) == list:
            for gid in sgid:
                self._query('servergroupaddclient sgid={} cldbid={}'.format(
                    gid, client_obj.client_database_id))
        logging.info('{} set the servergroup(s) of {} to {}'.format(
            featurename, client_obj.decoded_nickname, sgid))

    def clientaction_group_add(self, client_obj, featurename, sgid, **kwargs):
        ''' Add a client to servergroup (sgid) '''
        if not int(sgid) in self.client_servergroups:
            self._query('servergroupaddclient sgid={} cldbid={}'.format(
                sgid, client_obj.client_database_id))
            logging.info('{} added {} to sgid({})'.format(featurename, client_obj.decoded_nickname, sgid))

    def clientaction_group_del(self, client_obj, featurename, sgid, **kwargs):
        ''' Delete a client from servergroup (sgid) '''
        if int(sgid) in self.client_servergroups:
            self._query('servergroupdelclient sgid={} cldbid={}'.format(
                sgid, client_obj.client_database_id))
            logging.info('{} removed {} from sgid({})'.format(featurename, client_obj.decoded_nickname, sgid))

    @TelnetUtils.connected
    def _query(self, command):
        ''' For internal usage to simplify telnet queries '''
        self.tn.write('{}\n'.format(command))
        result = TelnetUtils.validate(self.tn.read_until('msg=ok', 2))
        return TelnetUtils.remove_linebreaks(result)

