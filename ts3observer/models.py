''' Here i will define some models to use '''

import logging
from utils import Escaper


class Client(object):

    def __init__(self, clid, telnet_lib):
        self.id = clid
        self.tn = telnet_lib

    #####
    # Actions

    def kick(self):
        logging.info('{} kicked {}'.format(self.executor, self.nickname))
        pass

    def move(self, target_channel_id=0, target_channel_pw=None):
        ocid = self.cid
        self.tn._query('clientmove clid={} cid={} cpw={}'.format(self.id, target_channel_id, Escaper.encode(target_channel_pw)))
        logging.info('{} moved {} from [{}] to [{}]'.format(
            self.executor,
            self.nickname,
            ocid,
            target_channel_id,
        ))
        pass

    def ban(self):
        logging.info('{} banned {} for {} seconds because of {}'.format(self.executor, self.nickname, 0, ''))
        pass

    def poke(self):
        logging.info('{} poked {} with message {}'.format(self.executor, self.nickname, ''))
        pass

    def msg(self):
        pass

    #####
    # properties

    def is_away(self):
        return int(self.away) == 1

    def is_idle(self):
        return int(self.idle_time) >= 1000

    def is_deaf(self):
        return int(self.output_muted) == 1

    def is_muted(self):
        return int(self.input_muted) == 1 or int(self.input_hardware) == 0

    def is_recording(self):
        return int(self.is_recording) == 1 or int(self.output_hardware) == 0

    def is_talker(self):
        return int(self.is_talker) == 1

    def is_channel_commander(self):
        return int(self.is_channel_commander) == 1

    def __repr__(self):
        dir(self)
        return '<Client uid={} name={}>'.format(self.unique_identifier, self.nickname)


class Channel(object):

    def __init__(self, cid, telnet_lib):
        self.id = cid
        self.tn = telnet_lib

    #####
    # Actions

    def edit(self):
        pass

    def delete(self):
        pass

    def move(self):
        pass

    def __repr__(self):
        return '<Channel cid={} name={}>'.format(self.cid, self.name)


class Action(object):
    ''' An action is a way to delay a method-call on a object like a client or
        a channel. It is recommended to use one.

        params:
            plugin_name:
                str   - The name of the Plugin which creates the action
            execute_run_id:
                int   - The run_id the action should be executed
            object_instance:
                obj   - Client or Channel, the Object on which the action should be executed
            function_name:
                str   - The name of the function on the object which should be executed
            function_args:
                tuple - A tuple of unnamed arguments for the function
            function_kwargs:
                dict  - A dictionary of named arguments for the function
            reason:
                str   - ONE WORD! If your plugin creates action for different needs (like IdleMover), it is recommended
                        to use a reason to distinguish between these. Otherwise you will get a confusing of your actions.
    '''

    def __init__(self, plugin_name, execute_run_id, object_instance, function_name, function_args=(), function_kwargs={}, reason='Undefined'):
        self.plugin_name = plugin_name
        self.created_run_id = ts3o.run_id
        self.execute_run_id = execute_run_id
        self.object_instance = object_instance
        self.object_instance_name = self.object_instance.__class__.__name__
        self.function_name = function_name
        self.function_args = function_args
        self.function_kwargs = function_kwargs
        self.reason = reason
        self.updated = True

    def register(self):
        if self in ts3o._action_queue:
            self.update()
        else:
            ts3o._action_queue.append(self)

    def update(self):
        for action in ts3o._action_queue:
            if action == self:
                action.updated = True
                break

    def execute(self):
        self.object_instance.executor = self.plugin_name
        getattr(self.object_instance, self.function_name)(*self.function_args, **self.function_kwargs)

    def __eq__(self, other):
        ''' https://docs.python.org/2/reference/datamodel.html#object.__eq__
            Is called at an 'in' statement (look at self.register)

            Raw comparison (without a str() call) won't work because it would recursively call __eq__
        '''
        return str(self.__repr__) == str(other.__repr__)

    def __ne__(self, other):
        return str(self.__repr__) != str(other.__repr__)

    def __repr__(self):
        ''' This is used to identify an action ... ugly, i know :( '''
        return '<Action P={} O={} R={} A={} oid={}>'.format(
            self.plugin_name,
            self.object_instance_name,
            self.reason,
            self.function_name,
            self.object_instance.id
        )

class Plugin(object):
    ''' Defines a basic plugin '''

    def __init__(self, config):
        self.config = config
        self.name = self.__class__.__name__

    def _setup(self):
        self.brain = ts3o.plugin_data[self.name]
        self.setup()

    def setup(self):
        ''' Could be used to implement a own __init__ '''
        pass

    def run(self, clients, channels, server_info):
        raise NotImplementedError('Your plugin should contain the \'run\' method!')
