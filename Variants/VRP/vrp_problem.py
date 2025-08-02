from qubo_helper import Qubo
from itertools import product

class VRPProblem:
    def __init__(self, sources, costs, time_costs, capacities, dests, weights):
        self.source_depot = 0
        self.costs = costs
        self.time_costs = time_costs
        self.capacities = capacities
        self.dests = dests
        self.weights = weights

    def get_qubo(self, vehicle_k_limits, only_one_const, order_const):
        """
        Generates the QUBO for the VRP based on the paper's formulation.
        Variables are tuples (i, j, k): vehicle i, destination j, step k.
        """
        num_vehicles = len(self.capacities)
        customer_nodes = self.dests

        qubo = Qubo()

        # ======================================================================
        # CONSTRAINT 1: Each customer is visited exactly once.
        # ======================================================================
        for j in customer_nodes:
            variables_for_dest_j = []
            for i in range(num_vehicles):
                k_max = vehicle_k_limits[i]
                for k in range(1, k_max + 1):
                    variables_for_dest_j.append((i, j, k))
            qubo.add_only_one_constraint(variables_for_dest_j, only_one_const)

        # ======================================================================
        # CONSTRAINT 2: Each vehicle is in at most one location at each step.
        # ======================================================================
        for i in range(num_vehicles):
            k_max = vehicle_k_limits[i]
            for k in range(1, k_max + 1):
                variables_for_vehicle_step = [(i, j, k) for j in customer_nodes]
                qubo.add_only_one_constraint(variables_for_vehicle_step, only_one_const)

        # ======================================================================
        # OBJECTIVE FUNCTION C: Minimize travel distance BETWEEN CUSTOMERS.
        # NOTE: Costs to/from the depot are handled classically in VRPSolution.
        # This simplifies the QUBO and is a robust hybrid approach.
        # ======================================================================
        for i in range(num_vehicles):
            k_max = vehicle_k_limits[i]
            # --- Cost between intermediate stops (step k to k+1) ---
            for k in range(1, k_max): # from step 1 up to k_max-1
                for j1 in customer_nodes:
                    for j2 in customer_nodes:
                        if j1 == j2: continue
                        var1 = (i, j1, k)
                        var2 = (i, j2, k+1)
                        cost = self.costs[j1][j2]
                        qubo.add((var1, var2), cost * order_const)
        
        return qubo
