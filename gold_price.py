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
        # 上海黄金交易所API
        self.sge_api_url = "https://www.sge.com.cn/graph/quotations"
        # 国际金价API
        self.international_api_url = "https://data-asg.goldprice.org/dbXRates/CNY"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def get_sge_gold_price(self):
        """获取上海黄金交易所金价"""
        try:
            response = requests.post(self.sge_api_url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                # 提取Au99.99黄金价格数据
                gold_data = None
                for item in data.get("list", []):
                    if item.get("instid") == "Au99.99":
                        gold_data = item
                        break
                
                if gold_data:
                    return {
                        "source": "上海黄金交易所",
                        "product": "Au99.99",
                        "price": float(gold_data.get("last")),
                        "unit": "元/克",
                        "change": float(gold_data.get("chg")),
                        "change_percent": float(gold_data.get("chgpct")),
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                return {"error": "未找到Au99.99数据"}
            else:
                return {"error": f"请求失败，状态码: {response.status_code}"}
        except Exception as e:
            return {"error": f"获取上海金价出错: {str(e)}"}
    
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
        sge_price = self.get_sge_gold_price()
        international_price = self.get_international_gold_price()
        
        return {
            "timestamp": int(time.time()),
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sge": sge_price,
            "international": international_price
        }
    
    def save_to_csv(self, filename="gold_price_history.csv"):
        """保存金价数据到CSV文件"""
        data = self.get_all_prices()
        
        # 创建一行数据
        row = {
            "timestamp": data["timestamp"],
            "datetime": data["datetime"],
        }
        
        # 添加上海金价数据
        if "error" not in data["sge"]:
            row["sge_price"] = data["sge"]["price"]
            row["sge_change"] = data["sge"]["change"]
            row["sge_change_percent"] = data["sge"]["change_percent"]
        else:
            row["sge_price"] = None
            row["sge_change"] = None
            row["sge_change_percent"] = None
        
        # 添加国际金价数据
        if "error" not in data["international"]:
            row["international_price_oz"] = data["international"]["price"]
            row["international_price_g"] = data["international"]["price_gram"]
        else:
            row["international_price_oz"] = None
            row["international_price_g"] = None
        
        # 转换为DataFrame
        df = pd.DataFrame([row])
        
        try:
            # 检查文件是否存在
            try:
                existing_df = pd.read_csv(filename)
                # 合并数据
                df = pd.concat([existing_df, df], ignore_index=True)
            except FileNotFoundError:
                # 文件不存在，使用新的DataFrame
                pass
            
            # 保存到CSV
            df.to_csv(filename, index=False)
            return {"success": True, "message": f"数据已保存到 {filename}"}
        except Exception as e:
            return {"success": False, "error": f"保存数据出错: {str(e)}"}


def print_gold_price():
    """打印金价信息"""
    tracker = GoldPriceTracker()
    data = tracker.get_all_prices()
    
    print("\n===== 实时金价信息 =====")
    print(f"获取时间: {data['datetime']}")
    
    # 打印上海金价
    print("\n上海黄金交易所:")
    if "error" not in data["sge"]:
        print(f"  产品: {data['sge']['product']}")
        print(f"  价格: {data['sge']['price']} {data['sge']['unit']}")
        print(f"  涨跌: {data['sge']['change']} ({data['sge']['change_percent']}%)")
    else:
        print(f"  获取失败: {data['sge']['error']}")
    
    # 打印国际金价
    print("\n国际金价:")
    if "error" not in data["international"]:
        print(f"  价格: {data['international']['price']} {data['international']['unit']}")
        print(f"  价格: {data['international']['price_gram']:.2f} {data['international']['unit_gram']}")
    else:
        print(f"  获取失败: {data['international']['error']}")
    
    # 保存数据
    save_result = tracker.save_to_csv()
    if save_result["success"]:
        print(f"\n{save_result['message']}")
    else:
        print(f"\n保存失败: {save_result['error']}")


if __name__ == "__main__":
    print_gold_price()