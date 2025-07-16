import pysnowball as ball

if __name__ == '__main__':
    ball.set_token("xq_a_token=59b7af07e856e0cbbe6a1db79e23dedd18b4d054;u=141750208076454")
    # res = ball.quotec('SZ002027')
    # res = ball.kline('SZ002027')
    res = ball.kline('SZ002027', 'week', 6)
    print(f"res :{res}")
