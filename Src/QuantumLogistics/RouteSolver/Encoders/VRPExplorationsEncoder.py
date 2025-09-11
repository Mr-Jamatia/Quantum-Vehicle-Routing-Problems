from dataclasses import dataclass

import numpy as np
from QuantumLogistics import Route
from .StandardEncoder import Encoder


@dataclass
class VRPInstance:
    clients_num: int
    vehicles_num: int
    cost_matrix: np.ndarray
    capacity: list
    demands: list
    xc: np.ndarray
    yc: np.ndarray


class VRPExplorationsEncoder(Encoder):
    def encode(self, route: Route):
        # to remember the route characteristics
        self.route = route

        coords = list(zip(*route.coords))
        self.vrp_instance = VRPInstance(
            clients_num=route.graph.N,
            vehicles_num=route.vehicles,
            cost_matrix=route.graph.W.toarray(),
            capacity=route.truckCapacity,
            demands=route.nodeCapacities,
            xc=np.array(coords[0]),
            yc=np.array(coords[1]),
        )

        return self.vrp_instance

    def extract(self, solution, verbose=False) -> list:
        solution, variables = solution

        routeSol = []
        for i in range(solution.shape[0]):
            var_list = np.transpose(variables[i]).reshape(-1)
            sol_list = np.transpose(solution[i]).reshape(-1)
            active_vars = [var_list[k] for k in range(len(var_list)) if sol_list[k] == 1]
            route = [int(var.split('.')[2]) for var in active_vars]
            edgelist = [(0, route[0])] + [(route[j], route[j + 1]) for j in range(len(route) - 1)] + [(route[-1], 0)]
            routeSol.append(edgelist)

        return routeSol
