from time import sleep

from my_finance.data_center import stock_dao, stock_client
from my_finance.data_center.stock_client import PAGE_SIZE


def fetch_and_save_stock_data(page_no) -> bool:
    try:
        stock_list = stock_client.fetch_stock_data(page_no)
        if not stock_list:
            print("No stock list found in the response.")
            return False
        stock_dao.batch_insert_quotes(stock_list)
        if len(stock_list) < PAGE_SIZE:
            return False
        return True
    except Exception as e:
        print(f"Failed to parse JSON response: {e}")
        return False


def main():
    page_no = 0
    while True:
        page_no += 1
        has_next = fetch_and_save_stock_data(page_no)
        if not has_next:
            break
        sleep(5)


if __name__ == '__main__':
    main()
