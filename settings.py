import json


def read():
    with open('/home/pi/tmp/flasky/config.json') as cfg_file:
        return json.load(cfg_file)


settings_json = read()


def refresh():
    global settings_json
    settings_json = read()


def coffee_timeout_millis():
    refresh()
    return int(settings_json['coffee']['timeout_minutes'] * 60)
