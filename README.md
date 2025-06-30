

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
uv run python main.py
```
