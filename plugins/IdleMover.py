from ts3observer.models import Plugin, Action


class Meta:
    author = 'Tim Fechner'
    version = '0.1'


class IdleMover(Plugin):

    default_config = {
        'afk_channel_id': 0
    }

    def run(self, clients, channels, server_info):
        pass
