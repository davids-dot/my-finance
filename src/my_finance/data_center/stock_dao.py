import json
from datetime import date, datetime

from my_finance.data_center import stock_client
from mysql_util import get_cursor


def to_decimal(value, precision=2):
    try:
        return round(float(value), precision)
    except (ValueError, TypeError):
        return None


def to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


# 将毫秒级时间戳转换为日期对象
def ts_to_date(ts):
    if ts is None:
        return None
    try:
        # 时间戳是毫秒，需要除以1000
        return datetime.fromtimestamp(int(ts) / 1000).date()
    except (ValueError, TypeError):
        return None


def clean_stock_data(stock_item: dict) -> dict:
    """
    将从 API 获取的单个股票字典清洗并转换为符合数据库表结构的字典。

    Args:
        stock_item: API 返回的 'list' 中的一个元素。

    Returns:
        一个处理过的、可以直接插入数据库的字典。
    """
    cleaned_data = {
        "symbol": stock_item.get("symbol"),
        "name": stock_item.get("name"),
        "current_price": to_decimal(stock_item.get("current"), 2),
        "change_pct": to_decimal(stock_item.get("percent"), 2),
        "change_amt": to_decimal(stock_item.get("chg"), 2),
        "volume": to_int(stock_item.get("volume")),
        "amount": to_decimal(stock_item.get("amount"), 2),
        "turnover_rate": to_decimal(stock_item.get("turnover_rate"), 2),
        "market_cap": to_int(stock_item.get("market_capital")),
        "float_market_cap": to_int(stock_item.get("float_market_capital")),
        "pe_ttm": to_decimal(stock_item.get("pe_ttm"), 2),
        "pb_ttm": to_decimal(stock_item.get("pb_ttm"), 2),
        "roe_ttm": to_decimal(stock_item.get("roe_ttm"), 4),
        "dividend_yield": to_decimal(stock_item.get("dividend_yield"), 4),
        "issue_date": ts_to_date(stock_item.get("issue_date_ts")),
        "followers": to_int(stock_item.get("followers")),
        "record_date": date.today()  # 使用当前日期作为记录日期
    }
    return cleaned_data


def clean_financial_data(stock_item: dict) -> dict:
    return {
        "symbol": stock_item.get("symbol"),
        "record_date": date.today(),
        "net_profit_cagr": to_decimal(stock_item.get("net_profit_cagr"), 4),
        "income_cagr": to_decimal(stock_item.get("income_cagr"), 4),
        "ps_ttm": to_decimal(stock_item.get("ps"), 4),
        "pcf_ttm": to_decimal(stock_item.get("pcf"), 4),
        "eps_ttm": to_decimal(stock_item.get("eps"), 2),
        "main_net_inflows": to_decimal(stock_item.get("main_net_inflows"), 2),
        "north_net_inflow": to_decimal(stock_item.get("north_net_inflow"), 2),
        "volume_ratio": to_decimal(stock_item.get("volume_ratio"), 2),
        "amplitude": to_decimal(stock_item.get("amplitude"), 2),
        "total_shares": to_int(stock_item.get("total_shares")),
        "float_shares": to_int(stock_item.get("float_shares")),
        "limitup_days": to_int(stock_item.get("limitup_days")),
        "lot_size": to_int(stock_item.get("lot_size")),
        "stock_type": to_int(stock_item.get("type"))
    }


def batch_insert_quotes_inner(quotes_data: list):
    """
    将清洗后的股票数据列表批量插入到数据库。
    使用 INSERT ... ON DUPLICATE KEY UPDATE 来处理重复数据。

    Args:
        quotes_data: 一个包含多个清洗后股票字典的列表。
    """
    if not quotes_data:
        print("No data to insert.")
        return

    # 构建 SQL 语句
    # 使用 IGNORE 会忽略重复的记录，不进行任何操作
    # 使用 ON DUPLICATE KEY UPDATE 会在记录已存在时进行更新
    sql = """
        INSERT INTO stock_quotes (
            symbol, name, current_price, change_pct, change_amt, volume, 
            amount, turnover_rate, market_cap, float_market_cap, pe_ttm, 
            pb_ttm, roe_ttm, dividend_yield, issue_date, followers, record_date
        ) VALUES (
            %(symbol)s, %(name)s, %(current_price)s, %(change_pct)s, %(change_amt)s, %(volume)s, 
            %(amount)s, %(turnover_rate)s, %(market_cap)s, %(float_market_cap)s, %(pe_ttm)s, 
            %(pb_ttm)s, %(roe_ttm)s, %(dividend_yield)s, %(issue_date)s, %(followers)s, %(record_date)s
        ) ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            current_price = VALUES(current_price),
            change_pct = VALUES(change_pct),
            change_amt = VALUES(change_amt),
            volume = VALUES(volume),
            amount = VALUES(amount),
            turnover_rate = VALUES(turnover_rate),
            market_cap = VALUES(market_cap),
            float_market_cap = VALUES(float_market_cap),
            pe_ttm = VALUES(pe_ttm),
            pb_ttm = VALUES(pb_ttm),
            roe_ttm = VALUES(roe_ttm),
            dividend_yield = VALUES(dividend_yield),
            followers = VALUES(followers),
            updated_at = NOW();
    """

    try:
        with get_cursor() as cursor:
            # 使用 executemany 进行批量插入
            row_count = cursor.executemany(sql, quotes_data)
            print(f"Successfully inserted or updated {row_count} rows.")
    except Exception as e:
        print(f"An error occurred during bulk insert: {e}")


def batch_insert_quotes(stock_list: list):
    # 3. 清洗数据
    # 使用列表推导式高效处理所有股票
    cleaned_quotes = [clean_stock_data(stock) for stock in stock_list]
    # 4. 批量插入数据库
    batch_insert_quotes_inner(cleaned_quotes)


def prepare_data_for_executemany(res):
    """
    将K-line API响应数据转换为适用于 cursor.executemany() 的格式。

    Args:
        res (dict): 从K-line API获取的原始字典格式的响应。

    Returns:
        tuple: 一个包含以下两个元素的元组：
            - sql (str): 参数化的 SQL INSERT...ON DUPLICATE KEY UPDATE 语句。
            - data (list): 一个由元组组成的列表，每个元组代表一行待插入的数据。
    """
    if res['error_code'] != 0 or 'data' not in res or not res['data'].get('item'):
        print("API响应数据有误或不包含任何项目。")
        return None, None

    data = res['data']
    symbol = data['symbol']
    api_columns = data['column']  # API响应中的列名
    items = data['item']

    # 定义数据库表的列的精确顺序。
    # 这确保了元组中的数据顺序与SQL占位符的顺序始终一致。
    db_columns = [
        'symbol', 'timestamp', 'volume', 'open', 'high', 'low', 'close', 'chg',
        'percent', 'turnoverrate', 'amount', 'volume_post', 'amount_post',
        'pe', 'pb', 'ps', 'pcf', 'market_capital', 'balance', 'hold_volume_cn',
        'hold_ratio_cn', 'net_volume_cn', 'hold_volume_hk', 'hold_ratio_hk',
        'net_volume_hk'
    ]

    # --- 1. 创建SQL模板字符串 ---

    # 为INSERT子句生成列名，格式如：`(col1, col2, ...)`
    insert_cols_str = ", ".join([f"`{col}`" for col in db_columns])

    # 为VALUES子句生成占位符，格式如：`(%s, %s, ...)`
    placeholders_str = ", ".join(["%s"] * len(db_columns))

    # 生成当唯一键（UNIQUE KEY）冲突时使用的UPDATE子句
    # 格式如：`col1 = VALUES(col1), col2 = VALUES(col2), ...`
    # 注意：作为唯一键的 symbol 和 timestamp 不应该被更新
    update_pairs = [f"`{col}` = VALUES(`{col}`)" for col in db_columns if col not in ['symbol', 'timestamp']]
    update_str = ", ".join(update_pairs)

    # 将所有部分组合成最终的SQL语句
    sql_template = (
        f"INSERT INTO `stock_weekly_kline` ({insert_cols_str}) "
        f"VALUES ({placeholders_str}) "
        f"ON DUPLICATE KEY UPDATE {update_str};"
    )

    # --- 2. 创建数据元组列表 ---

    quotes_data = []
    for row_values in items:
        # 创建一个字典，以便通过列名轻松查找对应的值
        row_dict = dict(zip(api_columns, row_values))
        processed_values = []
        for col in db_columns[1:]:  # 从'timestamp'开始遍历
            value = row_dict.get(col, None)

            # 检查当前列是否是时间戳列，并且值不为空
            if col == 'timestamp' and value is not None:
                # 1. 将毫秒时间戳除以1000得到秒
                # 2. 使用 fromtimestamp 转换为 datetime 对象
                # 3. 使用 strftime 格式化为 'YYYY-MM-DD' 字符串
                date_str = datetime.fromtimestamp(value / 1000).strftime('%Y-%m-%d')
                processed_values.append(date_str)
            else:
                processed_values.append(value)

        # 按照 db_columns 定义的顺序，为当前行准备一个数据元组
        # 我们从 db_columns 的第二个元素开始迭代，因为第一个元素 'symbol' 需要单独处理
        full_row_tuple = (symbol,) + tuple(processed_values)
        quotes_data.append(full_row_tuple)

    return sql_template, quotes_data


def fetch_and_save_kline_data(symbol, period='day', count=284):
    try:
        res = stock_client.fetch_kine(symbol, period, count)
        sql, quotes_data = prepare_data_for_executemany(res)

        if sql and quotes_data:
            # Print the results to verify
            print("--- Generated SQL Template ---")
            print(sql)
            print("\n--- Generated Data for executemany (first 2 rows) ---")
            for row in quotes_data:
                print(row)

            # Now, use them in your database code
            # (Assuming get_cursor() is your function to get a database cursor)
            print("\n--- Database Execution Block ---")
            try:
                with get_cursor() as cursor:
                    row_count = cursor.executemany(sql, quotes_data)
                    print(f"Successfully inserted or updated {row_count} rows.")
            except Exception as e:
                print(f"An error occurred during bulk insert: {e}")
    except Exception as e:
        print(f"Failed to parse JSON response: {e}")
        return None


def _test_batch_insert_quotes():
    """
        主函数，模拟从获取数据到存入数据库的完整流程。
        """
    # 1. 假设这是你从 API 获取的 JSON 响应字符串
    json_response_str = """
        {"data": {"count": 5000, "list": [{"symbol": "SZ300436", "net_profit_cagr": 33.64344403893904, "north_net_inflow": 0.0, "ps": 19.5141, "type": 11, "percent": 20.01, "has_follow": false, "tick_size": 0.01, "pb_ttm": 24.652, "float_shares": 136719819, "current": 51.34, "amplitude": 17.13, "pcf": 382.5311, "current_year_percent": 57.15, "float_market_capital": 7019195507.0, "north_net_inflow_time": 1751472000000, "market_capital": 8176767780.0, "dividend_yield": null, "lot_size": 100, "roe_ttm": -40.82648601552229, "total_percent": 303.97, "percent5m": 0.0, "income_cagr": -2.373891317521437, "amount": 1715428301.44, "chg": 8.56, "issue_date_ts": 1429632000000, "eps": -1.07, "main_net_inflows": 105709014.0, "volume": 35678826, "volume_ratio": 3.2, "pb": 24.652, "followers": 31096, "turnover_rate": 26.1, "mapping_quote_current": null, "first_percent": 44.01, "name": "广生堂", "pe_ttm": null, "dual_counter_mapping_symbol": null, "total_shares": 159267000, "limitup_days": 2}, {"symbol": "SH688068", "net_profit_cagr": -1.3427361548295935, "north_net_inflow": 0.0, "ps": 37.0078, "type": 82, "percent": 20.0, "has_follow": false, "tick_size": 0.01, "pb_ttm": 6.052, "float_shares": 92707940, "current": 194.81, "amplitude": 15.4, "pcf": null, "current_year_percent": 215.02, "float_market_capital": 18060433791.0, "north_net_inflow_time": 1751472000000, "market_capital": 18060433791.0, "dividend_yield": 0.102, "lot_size": 1, "roe_ttm": -7.029850849918811, "total_percent": 247.73, "percent5m": 0.0, "income_cagr": -51.32225645098609, "amount": 984120308.0, "chg": 32.47, "issue_date_ts": 1569772800000, "eps": -2.37, "main_net_inflows": 30353123.25999999, "volume": 5263796, "volume_ratio": 1.64, "pb": 6.037, "followers": 30897, "turnover_rate": 5.68, "mapping_quote_current": null, "first_percent": 140.63, "name": "热景生物", "pe_ttm": null, "dual_counter_mapping_symbol": null, "total_shares": 92707940, "limitup_days": 1}]}}
        """

    # 2. 解析 JSON
    try:
        api_data = json.loads(json_response_str)
        stock_list = api_data.get("data", {}).get("list", [])
        if not stock_list:
            print("No stock list found in the response.")
            return
        batch_insert_quotes(stock_list)

    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {e}")
        return


def main():
    fetch_and_save_kline_data('SZ300436', 'day', 284)


if __name__ == '__main__':
    main()
