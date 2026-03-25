# models.py
class Item:
    """单个物品"""
    def __init__(self, item_set_id, item_id, weight, value):
        self.item_set_id = item_set_id
        self.item_id = item_id          # 1,2,3
        self.weight = weight
        self.value = value

    def __repr__(self):
        return f"Item(set={self.item_set_id}, id={self.item_id}, w={self.weight}, v={self.value})"


class ItemSet:
    """一个项集，包含3个物品"""
    def __init__(self, set_id, items):
        self.set_id = set_id
        self.items = items               # list of 3 Item objects
        # 第三项的价值/重量比
        self.ratio = items[2].value / items[2].weight if items[2].weight > 0 else 0

    def get_ratio(self):
        return self.ratio

    def __repr__(self):
        return f"ItemSet({self.set_id}, ratio={self.ratio:.4f})"


class KnapsackData:
    """整个背包问题实例的数据"""
    def __init__(self, name, n_sets, capacity, item_sets):
        self.name = name
        self.n_sets = n_sets
        self.capacity = capacity
        self.item_sets = item_sets        # List[ItemSet]

    def sort_by_ratio(self):
        """按项集第三项的价值/重量比非递增排序"""
        self.item_sets.sort(key=lambda x: x.get_ratio(), reverse=True)