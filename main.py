import os
import telegram
import requests

from time import sleep
from datetime import datetime
from configparser import ConfigParser

config = ConfigParser()
config.read('./config.ini', encoding='UTF-8')

POLLING_IP = config.get('main', 'polling_ip')
CHANNEL_ID = config.get('main', 'channel_id')
DATETIME_FORMAT = config.get('runtime', 'datetime_format')

NO_RESPONSE_TEXT = f"{config.get('main', 'no_response_text')}"
SUCCESS_RESPONSE_TEXT = f"{config.get('main', 'success_response_text')}"

TG_BOT_TOKEN = config.get('main', 'tg_bot_token')
TG_API_BASE = config.get('main', 'tg_api_base')
TG_PARSE_MODE = config.get('main', 'tg_parse_mode')


def start_polling() -> None:

    last_check_res, last_checkstatus_changetime = read_last_check_values()

    while True:

        ping_response = os.system("ping -c 1 " + POLLING_IP + " > /dev/null 2>&1")

        if last_check_res != ping_response:

            cur_time = datetime.now()
            timedelta_seconds = (cur_time - last_checkstatus_changetime).total_seconds()
            timedelta_string = format_timedelta_string(timedelta_seconds)

            post_status_update(ping_response, timedelta_string)
            last_checkstatus_changetime = cur_time
            save_check_results(ping_response, last_checkstatus_changetime)

        last_check_res = ping_response
        sleep(60)


def read_last_check_values():
    last_check_res = None
    last_checkstatus_changetime = None
    try:
        last_check_res = config.getint('runtime', 'last_check_res')
        last_checkstatus_changetime = datetime.strptime(config.get('runtime', 'last_checkstatus_changetime'), DATETIME_FORMAT)
    except ValueError:
        pass

    if last_check_res is None: last_check_res = 0
    if last_checkstatus_changetime is None: last_checkstatus_changetime = datetime.now()

    return last_check_res, last_checkstatus_changetime


def save_check_results(last_check_res, last_checkstatus_changetime):

    config.set('runtime', 'last_check_res', str(last_check_res))
    config.set('runtime', 'last_checkstatus_changetime', datetime.strftime(last_checkstatus_changetime, DATETIME_FORMAT))

    with open('./config.ini', 'w') as configfile:
        config.write(configfile)


def format_timedelta_string(timedelta_seconds) -> str:

    timedelta_string = ""

    hours, remainder = divmod(timedelta_seconds, 3600)

    if int(hours) == 1: timedelta_string += '1 HOUR'
    if int(hours) > 1: timedelta_string += '{:1} HOURS'.format(int(hours))

    minutes, seconds = divmod(remainder, 60)

    if int(minutes) != 0:
        if int(hours) != 0: timedelta_string += ', '
        if int(minutes) == 1: timedelta_string += '1 MINUTE'
        if int(minutes) > 1: timedelta_string += '{:1} MINUTES'.format(int(minutes))

    #if int(seconds) != 0:
    #    if int(hours) != 0 or int(minutes) != 0: timedelta_string += ', '
    #    if int(seconds) == 1: timedelta_string += '1 second'
    #    if int(seconds) > 1: timedelta_string += '{:1} seconds'.format(int(seconds))

    return timedelta_string


def post_status_update(status_code, timedelta) -> None:
    response_text = None
    if status_code != 0:
        response_text = NO_RESPONSE_TEXT + "\n⏱ " + "UPTIME: {0}".format(timedelta)
        requests.post(f"{TG_API_BASE}{TG_BOT_TOKEN}/sendMessage?chat_id={CHANNEL_ID}&text={response_text}&parse_mode={TG_PARSE_MODE}")
        return
    response_text = SUCCESS_RESPONSE_TEXT + "\n⏱ " + "DOWNTIME: {0}".format(timedelta)
    requests.post(f"{TG_API_BASE}{TG_BOT_TOKEN}/sendMessage?chat_id={CHANNEL_ID}&text={response_text}&parse_mode={TG_PARSE_MODE}")


def main() -> None:
    start_polling()


if __name__ == '__main__':
    main()