# plotter.py
import matplotlib.pyplot as plt
from models import KnapsackData

def plot_scatter(data, instance_name):
    """绘制当前实例中所有物品的重量-价值散点图"""
    weights = []
    values = []
    for item_set in data.item_sets:
        for item in item_set.items:
            weights.append(item.weight)
            values.append(item.value)

    plt.figure(figsize=(10, 6))
    plt.scatter(weights, values, c='blue', alpha=0.6, edgecolors='w', s=50)
    plt.title(f"Scatter Plot of {instance_name}")
    plt.xlabel("Weight")
    plt.ylabel("Value")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.show()