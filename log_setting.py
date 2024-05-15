import logging
import time
import connection


# 自定义 Formatter 类，重写 formatTime 方法以使用 UTC+8 时间
class UTC8Formatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        # 将时间转换为 UTC+8，首先获取 UTC 时间，然后加上 8 小时的偏移
        utc_time = time.gmtime(record.created + 8 * 3600)
        if datefmt:
            return time.strftime(datefmt, utc_time)
        else:
            return time.strftime("%Y-%m-%d %H:%M:%S", utc_time)


# 创建 logger 实例
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 创建 console handler
ch = logging.StreamHandler()

# 设置自定义的 Formatter
formatter = UTC8Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# 添加 handler 到 logger
logger.addHandler(ch)

# conn = connection.connect_to_mysql()
# cur = conn.cursor()


# 定义日志记录函数，使用 logger 实例来记录日志
def log_debug(msg):
    logger.debug(msg)


def log_info(msg):
    logger.info(msg)


def log_warning(msg):
    logger.warning(msg)


def log_error(msg):
    logger.error(msg)
    # sql = "INSERT INTO error_log (message) VALUES (%s);"
    # cur.execute(sql, (msg,))
    # conn.commit()


def log_critical(msg):
    logger.critical(msg)
