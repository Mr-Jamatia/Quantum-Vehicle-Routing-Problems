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
        # CONSTRAINT 3: A vehicle cannot visit the same customer twice.
        # ======================================================================
        for i in range(num_vehicles):
            k_max = vehicle_k_limits[i]
            for j in customer_nodes:
                # For this vehicle i and this customer j, get all possible steps k
                variables_for_vehicle_dest = [(i, j, k) for k in range(1, k_max + 1)]
                
                # Add a penalty for any pair of these variables being 1,
                # which means visiting the same customer at two different steps.
                for k1_idx in range(len(variables_for_vehicle_dest)):
                    for k2_idx in range(k1_idx + 1, len(variables_for_vehicle_dest)):
                        var1 = variables_for_vehicle_dest[k1_idx]
                        var2 = variables_for_vehicle_dest[k2_idx]
                        # Use the same strong penalty
                        qubo.add((var1, var2), only_one_const)

        # ======================================================================
        # OBJECTIVE FUNCTION C: Minimize travel distance BETWEEN CUSTOMERS.
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
