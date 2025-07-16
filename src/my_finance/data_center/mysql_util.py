# mysql_util.py

import pymysql
from dbutils.pooled_db import PooledDB
from contextlib import contextmanager

# 导入配置
from my_finance.data_center.config import DB_CONFIG

class MySQLConnectionPool:
    """
    MySQL 数据库连接池管理类
    """
    _instance = None  # 用于存储单例实例
    _pool = None      # 用于存储连接池对象

    def __new__(cls, *args, **kwargs):
        """
        使用 __new__ 方法实现单例模式。
        确保整个应用生命周期中只有一个 MySQLConnectionPool 实例。
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_pool()
        return cls._instance

    def _initialize_pool(self):
        """
        初始化数据库连接池。
        """
        if self._pool is None:
            try:
                self._pool = PooledDB(
                    creator=pymysql,  # 指定使用 pymysql 作为数据库驱动
                    # 连接池参数
                    mincached=2,      # 初始时，连接池中至少创建的空闲的连接，0表示不创建
                    maxcached=5,      # 连接池中最多闲置的连接，0和None表示不限制
                    maxconnections=10, # 连接池允许的最大连接数，0和None表示不限制
                    maxshared=3,      # 连接池中最多共享的连接数量，0和None表示全部共享
                    blocking=True,    # 连接池中如果没有可用连接后，是否阻塞等待
                    maxusage=None,    # 一个连接最多被重复使用的次数，None表示无限制
                    setsession=[],    # 开始会话前执行的命令列表
                    # 数据库连接参数
                    **DB_CONFIG,
                    cursorclass=pymysql.cursors.DictCursor # 返回字典形式的游标
                )
                print("MySQL connection pool initialized successfully.")
            except Exception as e:
                print(f"Error initializing MySQL connection pool: {e}")
                raise

    def get_connection(self):
        """
        从连接池中获取一个连接。
        """
        if self._pool is None:
            self._initialize_pool()
        try:
            return self._pool.connection()
        except Exception as e:
            print(f"Error getting connection from pool: {e}")
            return None

    @staticmethod
    def close_connection(conn, cursor=None):
        """
        将连接归还给连接池。
        注意：PooledDB 的 connection() 返回的连接对象有自己的 close() 方法，
        调用它实际上是把连接放回池中，而不是真正关闭。
        """
        if cursor:
            try:
                cursor.close()
            except Exception as e:
                print(f"Error closing cursor: {e}")
        if conn:
            try:
                conn.close() # 实际上是归还连接到池中
            except Exception as e:
                print(f"Error returning connection to pool: {e}")


# 创建一个全局的连接池实例
mysql_pool = MySQLConnectionPool()

@contextmanager
def get_cursor():
    """
    一个上下文管理器，用于自动获取和释放数据库连接和游标。
    这是推荐的使用方式。

    Usage:
        with get_cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            result = cursor.fetchall()
    """
    conn = None
    cursor = None
    try:
        conn = mysql_pool.get_connection()
        if conn:
            cursor = conn.cursor()
            yield cursor
        else:
            raise Exception("Failed to get database connection.")
    except Exception as e:
        print(f"Database operation error: {e}")
        # 如果需要，可以在这里回滚事务
        # if conn:
        #     conn.rollback()
        raise
    finally:
        if conn and cursor:
            # 提交事务
            conn.commit()
        # 将连接归还到池中
        mysql_pool.close_connection(conn, cursor)


# --- 对外提供的接口 ---

def get_db_connection():
    """
    直接获取一个连接对象，需要手动管理。
    适用于需要手动控制事务的复杂场景。
    """
    return mysql_pool.get_connection()

def close_db_connection(conn, cursor=None):
    """
    手动归还连接。
    """
    mysql_pool.close_connection(conn, cursor)