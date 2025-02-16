import os
import sqlite3
import logging
from dotenv import load_dotenv

load_dotenv()
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class VerboseCursor(sqlite3.Cursor):
    """
    增加一个VerboseCursor装饰类,可以输出语句,记录日志
    """

    def __init__(self, connection: sqlite3.Connection):
        super().__init__(connection)
        self.logger = self._setup_logger()

    def _setup_logger(self):
        """
        设置日志记录器
        """
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def safe_format_sql(self, sql, parameters):
        """
        安全地格式化 SQL 语句,用于打印目的
        """
        parameterized_sql = sql
        if parameters:
            for param in parameters:
                parameterized_sql = parameterized_sql.replace("?", repr(param), 1)
        return parameterized_sql

    def execute(self, sql, parameters=None):
        """
        执行 SQL 语句,并记录日志
        """
        self.logger.debug(
            f"Executing SQL statement: {self.safe_format_sql(sql, parameters)}"
        )
        try:
            if parameters:
                super().execute(sql, parameters)
            else:
                super().execute(sql)
            return True
        except sqlite3.Error as e:
            self.logger.error(f"An error occurred: {e}")
            return False


def execute_sqlite_sql(sql, param=None, should_print=False):
    """
    执行 SQLite SQL 语句,并返回结果

    :param sql: SQL 语句
    :param param: SQL 语句的参数
    :param should_print: 是否打印结果
    :return: 查询结果或 None
    """
    db_path = os.getenv("SQL_LITE_DB_PATH", "./pdf_deal_log.db")
    conn = sqlite3.connect(db_path)
    c = VerboseCursor(conn)

    try:
        if not c.execute(sql, param):
            conn.rollback()
            return None

        results = c.fetchall()
        if should_print:
            for row in results:
                print(row)

        conn.commit()
        return results
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        conn.rollback()
        return None
    finally:
        c.close()
        conn.close()
