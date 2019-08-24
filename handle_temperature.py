import logging
import configparser
import sys
import datetime
import sqlite3
from contextlib import closing
from messaging_slack import notice 

config = configparser.ConfigParser()
config.read('config')

SUCCESS = config['STATUS']['SUCCESS']
ERROR = config['STATUS']['ERROR']
COUNT_DEFAULT = config['ERROR_COUNT']['DEFAULT']
COUNT_LIMIT = config['ERROR_COUNT']['LIMIT']
DB = config['DB']['file']
log_file = config['LOG']['file']

THRESHOLD = 33.0

NOTICE_MESSAGE = "<!channel> 室温が {} 度になりました。"
ERROR_MESSAGE = "<!channel> デバイスに接続できません。"

logger = logging.getLogger(__name__)
fmt = "%(asctime)s %(levelname)s :%(message)s"
logging.basicConfig(level=logging.DEBUG, format=fmt, filename=log_file)


def error_check(flg):
    if flg == SUCCESS:
        update_error_count()
    else:
        error_count = get_error_count()
        error_count += 1

        if error_count == COUNT_LIMIT:
            notice(ERROR_MESSAGE.format(t))
            logger.error(ERROR_MESSAGE.format(datetime.datetime.now()))

        update_error_count(error_count)

def get_error_count():
    with closing(sqlite3.connect(DB)) as conn:
        cursor = conn.cursor()
        cursor.execute("select count from error_counts")
        res =  cursor.fetchone()
        conn.close()
        return res[0]

def update_error_count(error_count=COUNT_DEFAULT):
    with closing(sqlite3.connect(DB)) as conn:
        cursor = conn.cursor()
        sql = "update error_counts set count = ?, updated_at = ?"
        cursor.execute(sql, (error_count, datetime.datetime.now()))
        conn.commit()
        conn.close()

def str_add(s, num):
    i = int(s)
    i += num
    return str(i)

if __name__ == "__main__":
    args = sys.argv

    try:
        t = args[1]
        t = float(t)
        error_check(ERROR)
    except:
        error_check(ERROR)
        logger.error(ERROR_MESSAGE.format(datetime.datetime.now()))
        exit()

    if t > THRESHOLD:
        message = NOTICE_MESSAGE
        notice(message.format(t))

    with closing(sqlite3.connect(DB)) as conn:
        cursor = conn.cursor()
        sql = "insert into temperature (temperature, created_at) values (?, ?)"
        now = datetime.datetime.now()
        cursor.execute(sql, (t, now.strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        conn.close()
