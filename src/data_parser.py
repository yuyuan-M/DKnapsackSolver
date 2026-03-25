# data_parser.py
import re
from models import Item, ItemSet, KnapsackData

def parse_knapsack_file(filepath):
    """
    解析数据文件，返回 KnapsackData 对象列表
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    instances = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # 查找实例标题，例如 "IDKP1:"
        if re.match(r'^[A-Z]+[0-9]+:', line):
            name = line.rstrip(':')
            i += 1
            # 寻找包含容量信息的行
            while i < len(lines) and "cubage of knapsack is" not in lines[i]:
                i += 1
            if i >= len(lines):
                break
            cap_line = lines[i]
            cap_match = re.search(r'is\s+(\d+)', cap_line)
            capacity = int(cap_match.group(1)) if cap_match else 0
            i += 1

            # 寻找利润行
            while i < len(lines) and "profit of items are:" not in lines[i]:
                i += 1
            if i >= len(lines):
                break
            i += 1
            profit_vals = []
            while i < len(lines) and not re.match(r'^The weight', lines[i]) and not re.match(r'^[A-Z]+[0-9]+:', lines[i]):
                nums = re.findall(r'\d+', lines[i])
                profit_vals.extend([int(x) for x in nums])
                i += 1

            # 寻找重量行
            while i < len(lines) and "weight of items are:" not in lines[i]:
                i += 1
            if i >= len(lines):
                break
            i += 1
            weight_vals = []
            while i < len(lines) and not re.match(r'^[A-Z]+[0-9]+:', lines[i]) and lines[i].strip() != '':
                nums = re.findall(r'\d+', lines[i])
                weight_vals.extend([int(x) for x in nums])
                i += 1

            # 构建项集
            n_sets = len(profit_vals) // 3
            item_sets = []
            for idx in range(n_sets):
                base = idx * 3
                items = [
                    Item(idx, 1, weight_vals[base], profit_vals[base]),
                    Item(idx, 2, weight_vals[base+1], profit_vals[base+1]),
                    Item(idx, 3, weight_vals[base+2], profit_vals[base+2])
                ]
                item_sets.append(ItemSet(idx, items))
            instances.append(KnapsackData(name, n_sets, capacity, item_sets))
        else:
            i += 1
    return instances