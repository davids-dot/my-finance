import pysnowball as ball

import requests

token = '59b7af07e856e0cbbe6a1db79e23dedd18b4d054'

# 设置token
ball.set_token(f"xq_a_token={token};u=141750208076454")
cookies = {
    'xqat': token,
}

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9,ko;q=0.8,en;q=0.7',
    'cache-control': 'no-cache',
    'origin': 'https://xueqiu.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://xueqiu.com/',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
}

PAGE_SIZE = 30


def get_params(page_no):
    params = {
        'page': page_no,
        'size': PAGE_SIZE,
        'order': 'desc',
        'order_by': 'percent',
        'market': 'CN',
        'type': 'sh_sz',
    }
    return params


def fetch_stock_data(page_no) -> list | None:
    try:
        params = get_params(page_no)
        response = requests.get(
            'https://stock.xueqiu.com/v5/stock/screener/quote/list.json',
            params=params,
            cookies=cookies,
            headers=headers,
        )
        api_data = response.json()
        return api_data.get("data", {}).get("list", [])
    except Exception as e:
        print(f"Failed to parse JSON response: {e}")
        return None


def fetch_kine(symbol, period='day', count=284):
    return ball.kline(symbol, period, count)


def real_time_quote(symbols):
    return ball.quotec(symbols)


def main():
    quote = real_time_quote('SZ002911')
    print(quote)


if __name__ == '__main__':
    main()
