import requests

cookies = {
    'xqat': '59b7af07e856e0cbbe6a1db79e23dedd18b4d054',
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

params = {
    'page': '1',
    'size': '30',
    'order': 'desc',
    'order_by': 'percent',
    'market': 'CN',
    'type': 'sh_sz',
}


def main():
    response = requests.get(
        'https://stock.xueqiu.com/v5/stock/screener/quote/list.json',
        params=params,
        cookies=cookies,
        headers=headers,
    )
    print(response.json())


if __name__ == '__main__':
    main()
