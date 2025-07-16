from my_finance.data_center import stock_client
import time

from my_finance.tools import notify_client
from my_finance.utils.obj_utils import JsonUtils


def in_order_time():
    # 当前时间为 9:30-11:30， 13:00-15:00 为交易时间
    current_time = time.localtime()
    hour = current_time.tm_hour
    minute = current_time.tm_min

    # 上午交易时间：9:30-11:30
    morning_trading = (hour == 9 and minute >= 30) or (hour == 10) or (hour == 11 and minute <= 30)

    # 下午交易时间：13:00-15:00
    afternoon_trading = (13 <= hour < 15)

    return morning_trading or afternoon_trading


def main(stock_code):
    # 每5分钟查询一次 单张股票的实时行情
    while True:
        try:
            if not in_order_time():
                print("当前不在交易时间")
                time.sleep(5 * 60)
                continue
            # 打印时间
            print("check at  " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            quote = stock_client.real_time_quote(stock_code)
            current = quote.get("data", {})[0].get("current", 0)
            if current < 10.20:
                notify_client.send_notification("买入通知", f"股票{stock_code}现价为{current}，请及时买入")
        except Exception as e:
            print(e)
        time.sleep(5 * 60)


if __name__ == '__main__':
    main('SZ002911')
