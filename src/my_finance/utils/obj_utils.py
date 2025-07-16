import time
import importlib
import threading
from sonyflake import SonyFlake


json = importlib.import_module('json')


class JsonUtils:

    @staticmethod
    def to_camel_case(snake_str: str) -> str:
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    @staticmethod
    def camel_case_encoder(obj):
        if obj is None:
            return obj
        if isinstance(obj, (str, int, float, bool)):
            return obj
        if isinstance(obj, list):
            return [JsonUtils.camel_case_encoder(item) for item in obj]
        if isinstance(obj, dict):
            return {JsonUtils.to_camel_case(key): JsonUtils.camel_case_encoder(value) 
                   for key, value in obj.items()}
        if hasattr(obj, '__dict__'):
            return JsonUtils.camel_case_encoder(obj.__dict__)
        return obj

    # json 解析函数,固定写法
    @staticmethod
    def default_encoder(obj):
        return obj.__dict__

    @staticmethod
    def is_json(unknown_str: str) -> bool:
        try:
            json.loads(unknown_str)
            return True
        except ValueError:
            return False

    @staticmethod
    def to_json(data) -> str:
        return json.dumps(data, ensure_ascii=False, default=JsonUtils.default_encoder)

    @staticmethod
    def to_camel_case_json(data) -> str:
        return json.dumps(JsonUtils.camel_case_encoder(data), ensure_ascii=False)

    @staticmethod
    def get_data(data_obj, key: str, default=None):
        if isinstance(data_obj, dict):
            return data_obj.get(key)
        elif hasattr(data_obj, key):
            return getattr(data_obj, key)
        else:
            return default


# 使用示例（无需初始化类）
if __name__ == "__main__":
    pass


class StringUtils:
    @staticmethod
    def is_blank(s: str) -> bool:
        """字符串是否为空"""
        return not (s and s.strip())


class DateUtils:
    @staticmethod
    def get_current_millisecond() -> int:
        """获取当前时间戳"""
        return time.time_ns() // 1_000_000


class IdUtils:
    _generator = None
    _lock = threading.Lock()

    @staticmethod
    def __get_generator():
        if IdUtils._generator is None:
            with IdUtils._lock:
                if IdUtils._generator is None:
                    IdUtils._generator = SonyFlake()
        return IdUtils._generator

    @staticmethod
    def next_snowflake_id() -> int:
        return IdUtils.__get_generator().next_id()
