# 实时金价查询工具

这是一个简单的Python工具，用于获取实时金价信息，包括上海黄金交易所的Au99.99金价和国际金价数据。

## 功能特点

- 获取上海黄金交易所Au99.99实时金价
- 获取国际金价（以人民币计价）
- 支持单次查询和持续监控模式
- 可将历史数据保存为CSV文件，方便后续分析

## 安装说明

本项目使用uv进行环境管理，确保您已安装Python 3.6+和uv工具。

```bash
# 克隆仓库
git clone <repository-url>
cd my-finance

# 创建虚拟环境并安装依赖
uv venv --seed
source .venv/bin/activate
uv pip install requests pandas
```

## 使用方法

### 单次查询金价

```bash
python main.py
```

### 监控模式（定期获取金价）

```bash
python main.py --monitor --interval 300  # 每5分钟更新一次
```

### 保存数据到CSV文件

```bash
python main.py --save --file gold_data.csv
```

### 监控并保存数据

```bash
python main.py --monitor --interval 600 --save  # 每10分钟更新并保存
```

## 命令行参数

- `-m, --monitor`: 启动监控模式，定期获取金价
- `-i, --interval`: 监控模式下的刷新间隔（秒），默认300秒
- `-s, --save`: 保存数据到CSV文件
- `-f, --file`: CSV文件名，默认为gold_price_history.csv

## 数据来源

- 上海黄金交易所官网
- 国际金价数据API

## 注意事项

- 本工具仅供参考，不构成任何投资建议
- 数据可能存在延迟，交易决策请以官方数据为准
- API可能会发生变化，如遇到数据获取失败，请检查API是否更新