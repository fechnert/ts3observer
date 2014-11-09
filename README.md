ts3observer
============

ts3-observer is a Feature based serverbot for [TeamSpeak3] servers.

It allows to observe specific servers and manage clients and channels.


Features
--------

* Move clients to specific channel on event
* Kick clients by name blacklist
* Detect musicbots and demote them


Requirements
------------

You need some additional packages to run ts3observer

* [pyaml]

```sh
sudo pip install pyaml
```

Usage
-----

The observer doesn't need to be installed.

But before you start, you should configure the features you want.

After that, you can run the mainfile to run the server.

```sh
./run.sh
```


[TeamSpeak3]:http://www.teamspeak.com/?page=teamspeak3
[pyaml]:https://pypi.python.org/pypi/pyaml