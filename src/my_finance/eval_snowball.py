import pysnowball as ball

if __name__ == '__main__':
    ball.set_token("xq_a_token=662745a236*****;u=909119****")
    res = ball.quotec('SZ002027')
    print(f"res :{res}")
