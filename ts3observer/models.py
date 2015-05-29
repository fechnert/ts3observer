''' Here i will define some models to use '''


class Client(object):

    def __init__(self, clid, telnet_lib):
        self.clid = clid
        self.tn = telnet_lib

    def kick(self):
        pass

    def move(self):
        pass

    def ban(self):
        pass

    def poke(self):
        pass

    def __repr__(self):
        dir(self)
        return '<Client uid={} name={}>'.format(self.unique_identifier, self.nickname)


class Channel(object):

    def __init__(self, cid, telnet_lib):
        self.cid = cid
        self.tn = telnet_lib

    def edit(self, **kwargs):
        pass

    def delete(self):
        pass

    def move(self, pid):
        pass

    def __repr__(self):
        return '<Channel cid={} name={}>'.format(self.cid, self.name)


class Action(object):
    pass
