#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
金价查询工具主程序
"""

import argparse
import time
from gold_price import GoldPriceTracker, print_gold_price


def main():
    """主函数，处理命令行参数并执行相应操作"""
    parser = argparse.ArgumentParser(description="实时金价查询工具")
    parser.add_argument("-m", "--monitor", action="store_true", help="启动监控模式，定期获取金价")
    parser.add_argument("-i", "--interval", type=int, default=300, help="监控模式下的刷新间隔（秒），默认300秒")
    parser.add_argument("-s", "--save", action="store_true", help="保存数据到CSV文件")
    parser.add_argument("-f", "--file", type=str, default="gold_price_history.csv", help="CSV文件名，默认为gold_price_history.csv")
    
    args = parser.parse_args()
    
    tracker = GoldPriceTracker()
    
    if args.monitor:
        print(f"启动金价监控，刷新间隔: {args.interval}秒")
        try:
            while True:
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
                if args.save:
                    save_result = tracker.save_to_csv(args.file)
                    if save_result["success"]:
                        print(f"\n{save_result['message']}")
                    else:
                        print(f"\n保存失败: {save_result['error']}")
                
                print(f"\n下次更新时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + args.interval))}")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n监控已停止")
    else:
        # 单次查询
        print_gold_price()


if __name__ == "__main__":
    main()