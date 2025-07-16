from my_finance.data_center import mysql_util


def main():
    # 执行查询，挑选出符合条件的股票
    with mysql_util.get_cursor() as cursor:
        cursor.execute("""  select * 
                            from stock_quotes
                            where 
                            -- 市值大于100亿
                            market_cap > 10000000000
                            -- 上市时间超过10年 
                            and issue_date <= DATE_SUB(CURDATE(), INTERVAL 10 YEAR)""")

        stock_list = cursor.fetchall()
        for stock_item in stock_list:
            if stock_item is None:
                continue
            print(f"stock_item is {stock_item}")


if __name__ == '__main__':
    main()
