from ts3observer.models import Plugin, Action


class Meta:
    author_name = 'Tim Fechner'
    author_email = 'tim.b.f@gmx.de'
    version = '0.2'


class IdleMover(Plugin):

    default_config = {
        'afk_channel_id': 0,
        'afk_channel_password': '',
        'lobby_channel_id': 0,
        'check_away': {
            'enable': True,
            'move_after': 0
        },
        'check_idle': {
            'enable': True,
            'move_after': 900
        },
        'check_deaf': {
            'enable': True,
            'move_after': 0
        },
        'check_muted': {
            'enable': False,
            'move_after': 1800
        }
    }

    def setup(self):
        self.brain.update({'move_origins':{}})

    def run(self, clients, channels, server_info):
        for clid, client in clients.items():
            if not any([
                self.check_away(client),
                self.check_idle(client),
                self.check_deaf(client),
                self.check_muted(client),
            ]):
                if self._in_afk_channel(client):
                    self.move_back(client)

    def check_away(self, client):
        if self.config['check_away']['enable']:
            if client.is_away() and not self._in_afk_channel(client):
                self.move(client, 'check_away')
                self.brain['move_origins'].update({int(client.id): int(client.cid)})
            if client.is_away():
                return True

    def check_idle(self, client):
        pass

    def check_deaf(self, client):
        if self.config['check_deaf']['enable']:
            if client.is_deaf() and not self._in_afk_channel(client):
                self.move(client, 'check_away')
                self.brain['move_origins'].update({int(client.id): int(client.cid)})
            if client.is_deaf():
                return True

    def check_muted(self, client):
        pass

    def move(self, client, function_name):
        Action(
            'IdleMover',
            ts3o.run_id + self.config[function_name]['move_after'],
            client,
            'move',
            function_kwargs = {
                'target_channel_id': self.config['afk_channel_id'],
                'target_channel_pw': self.config['afk_channel_password']
            },
            reason=function_name
        ).register()

    def move_back(self, client):
        if int(client.id) in self.brain['move_origins']:
            origin = self.brain['move_origins'][int(client.id)]
        else:
            origin = self.config['lobby_channel_id']

        Action(
            'IdleMover',
            ts3o.run_id,
            client,
            'move',
            function_kwargs = {
                'target_channel_id': origin,
                'target_channel_pw': self.config['afk_channel_password']
            },
            reason='move_back'
        ).register()

    def _in_afk_channel(self, client):
        return int(client.cid) == self.config['afk_channel_id']
