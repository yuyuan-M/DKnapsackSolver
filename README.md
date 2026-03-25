# D{0-1}KP 问题求解器

## 简介
本项目实现了 D{0-1}KP 问题的动态规划求解器，并提供图形界面。支持：
- 读取四种数据集（IDKP, SDKP, UDKP, WDKP）
- 绘制物品重量-价值散点图
- 按第三项价值/重量比排序
- 求解最优值并记录物品选择
- 导出结果为 TXT 或 Excel 文件

## 运行环境
- Python 3.8+
- 依赖库：matplotlib, openpyxl（可选，用于导出Excel）

## 安装依赖
```bash
pip install matplotlib openpyxl