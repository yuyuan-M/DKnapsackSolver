# solver.py
import time
from array import array

def solve_dp_with_selection(data, sorted_flag=False):
    """
    带选择记录的动态规划求解器。
    返回: (最优值, 选择列表, 耗时毫秒)
    选择列表: 长度为 n_sets 的列表，每个元素为 0-3，表示该项集选择的物品编号（0不选，1/2/3）
    """
    start = time.perf_counter()
    item_sets = data.item_sets
    if sorted_flag:
        item_sets = sorted(item_sets, key=lambda x: x.get_ratio(), reverse=True)

    capacity = data.capacity
    n = len(item_sets)

    # dp[w] 表示容量为 w 时的最大价值
    dp = [0] * (capacity + 1)

    # 记录每个项集在每个容量下的选择，使用 bytearray 节省内存（每个元素仅1字节）
    choices_per_item = []  # 每一项集对应一个 bytearray

    # 主循环：依次处理每个项集
    for item_set in item_sets:
        # 当前项集的选择记录，初始全0
        choice_row = bytearray(capacity + 1)
        # 保存上一轮 dp 状态，因为每个项集只能选一个物品，需要基于上一轮的状态
        prev = dp[:]

        # 倒序遍历容量，确保每个项集最多选一个物品
        for w in range(capacity, -1, -1):
            best = prev[w]  # 不选当前项集
            best_item = 0

            # 尝试选择当前项集中的三个物品
            for idx, item in enumerate(item_set.items, start=1):
                if w >= item.weight:
                    cand = prev[w - item.weight] + item.value
                    if cand > best:
                        best = cand
                        best_item = idx

            dp[w] = best
            choice_row[w] = best_item  # 记录达到容量 w 时本项集选择的物品编号

        choices_per_item.append(choice_row)

    # 回溯：根据记录的选择逆向构造解
    selection = [0] * n
    remaining = capacity
    for i in range(n - 1, -1, -1):
        choice = choices_per_item[i][remaining]  # 第 i 个项集在剩余容量下的选择
        selection[i] = choice
        if choice != 0:
            # 选中的物品，扣除其重量，继续回溯
            item = item_sets[i].items[choice - 1]
            remaining -= item.weight

    best_value = dp[capacity]
    elapsed = (time.perf_counter() - start) * 1000
    return best_value, selection, elapsed