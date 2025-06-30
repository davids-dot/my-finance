#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
获取实时金价的模块
"""

import requests
import pandas as pd
from datetime import datetime
import json
import time


class GoldPriceTracker:
    """金价追踪器类，用于获取实时金价数据"""

    def __init__(self):
        # 国际金价API
        self.international_api_url = "https://data-asg.goldprice.org/dbXRates/CNY"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def get_international_gold_price(self):
        """获取国际金价（以人民币计价）"""
        try:
            response = requests.get(self.international_api_url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                gold_data = data.get("items", [])[0] if data.get("items") else None

                if gold_data:
                    return {
                        "source": "国际金价",
                        "price": float(gold_data.get("xauPrice")),
                        "unit": "元/盎司",
                        "price_gram": float(gold_data.get("xauPrice")) / 31.1035,  # 转换为克价
                        "unit_gram": "元/克",
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                return {"error": "未找到国际金价数据"}
            else:
                return {"error": f"请求失败，状态码: {response.status_code}"}
        except Exception as e:
            return {"error": f"获取国际金价出错: {str(e)}"}

    def get_all_prices(self):
        """获取所有金价数据"""
        international_price = self.get_international_gold_price()

        return {
            "timestamp": int(time.time()),
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "international": international_price
        }


def print_gold_price():
    """打印金价信息"""
    tracker = GoldPriceTracker()
    data = tracker.get_all_prices()

    # 打印国际金价
    print("\n internation gold price:")
    if "error" not in data["international"]:
        print(f"  价格: {data['international']['price']} {data['international']['unit']}")
        print(f"  价格: {data['international']['price_gram']:.2f} {data['international']['unit_gram']}")
    else:
        print(f"  获取失败: {data['international']['error']}")


if __name__ == "__main__":
    print_gold_price()
