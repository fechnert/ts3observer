# ts3observer

The ts3observer (_teamspeak 3 observer_) is a plugin-based tool to observe a
[Teamspeak 3 Server]. It allows you to interact with clients, groups and
channels. For example, move clients if they are idle, kick clients with unwanted
nicknames or simply message a group if some client complaints about another.

For more information, examples and developer information, read the [Wiki].

# Installation

First you need to clone the tool:

```sh
git clone git@github.com:HWDexperte/ts3observer.git
```

After that, you need some requirements:

```sh
sudo apt-get install python python-yaml pip
pip install -r requirements.txt
```

# Configuration

After a successful installation, you need to configure the ts3observer with the
main configuration file unter `conf/`.

You should copy the `ts3observer.yml.skel` to `ts3observer.yml` and modify the
new file to match your settings.

# Usage

You can run the ts3observer with `python ts3observer.py run`.

To view all available commands, type `python ts3observer --help`

# Plugins

By default there are (currently) no plugins with real content available.
You can add plugins by copying the plugin.py in the `plugins/` folder while the
ts3observer is not running.

If you now start the ts3observer, it will "load" all plugins it can find in the
plugin folder.

If it finds any new plugins (plugins without a config file), it will create a
default config in the `conf/` folder, log the new plugin as '[NEW]' and stops
after all plugins are loaded and initialized to allow you to configure the new
created config files.

# Important notes

It is recommended to run the ts3observer locally on the server where your
teamspeak server in running. You can run it remotely, but then you have to write
the IP address of the remote server to teamspeak's `query_ip_whitelist.txt`.

To avoid all this mess, simply make sure that ts3observer is running beside the
teamspeak server and that a local IP adress like `localhost` or `127.0.0.1` is
written in teamspeak's `query_ip_whitelist.txt`. Should be by default.

[Teamspeak 3 Server]:http://www.teamspeak.com/?page=teamspeak3
[Wiki]:https://github.com/HWDexperte/ts3observer/wiki
