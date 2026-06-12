import pandas as pd

class VehicleRoutingSolution:
    def __init__(self, cluster: pd.DataFrame, path: list[int], totalCost: int):
        self.cluster = cluster
        self.path = path
        self.totalCost = totalCost

    cluster: pd.DataFrame
    path: list[int]
    totalCost: int

    