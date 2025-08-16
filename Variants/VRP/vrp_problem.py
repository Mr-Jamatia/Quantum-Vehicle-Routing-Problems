from qubo_helper import Qubo

class VRPProblem:
    def __init__(self, sources, costs, time_costs, capacities, dests, weights):
        self.source_depot = 0
        self.costs = costs
        self.time_costs = time_costs
        self.capacities = capacities
        self.dests = dests
        self.weights = weights

    def get_qubo_paper(self, vehicle_k_limits, A1, A2):
        """
        Generates the QUBO for the VRP as specified
        in the Gora et al. paper
        """
        num_vehicles = len(self.capacities)
        customer_nodes = self.dests
        depot_node = self.source_depot

        cost_qubo = Qubo()
        constraint_qubo = Qubo()

        # --- OBJECTIVE FUNCTION 'C' ---

        # Part 1: Cost from Depot to First Customer
        # Adds C(depot, i) if customer i is the first stop (k=1) for vehicle m.
        for m in range(num_vehicles):
            for i_cust_node in customer_nodes:
                cost = self.costs[depot_node][i_cust_node]
                var = (m, i_cust_node, 1)
                cost_qubo.add((var, var), cost)

        # Part 2: Cost between Intermediate Customers
        # Adds C(i, j) if vehicle m goes from customer i (at step k) to customer j (at step k+1).
        for m in range(num_vehicles):
            k_max = vehicle_k_limits[m]
            for k in range(1, k_max):
                for i_cust_node in customer_nodes:
                    for j_cust_node in customer_nodes:
                        if i_cust_node == j_cust_node: continue
                        cost = self.costs[i_cust_node][j_cust_node]
                        var1 = (m, i_cust_node, k)
                        var2 = (m, j_cust_node, k + 1)
                        cost_qubo.add((var1, var2), cost)

        # Part 3: Cost from Last Customer to DepoT
        # Adds C(i, depot) only if customer i is the last stop for vehicle m.
        # This is done by adding C(i,depot) as a linear term, and then subtracting it
        # via a quadratic term if another stop follows.
        for m in range(num_vehicles):
            k_max = vehicle_k_limits[m]
            for k in range(1, k_max + 1):
                for i_cust_node in customer_nodes:
                    cost_to_depot = self.costs[i_cust_node][depot_node]
                    var_i = (m, i_cust_node, k)
                    
                    # Add the cost as if this IS the last stop
                    cost_qubo.add((var_i, var_i), cost_to_depot)
                    
                    # If there's a NEXT stop, subtract the cost we just added
                    if k < k_max:
                        for j_cust_node in customer_nodes:
                            if i_cust_node == j_cust_node: continue
                            var_j_next = (m, j_cust_node, k + 1)
                            cost_qubo.add((var_i, var_j_next), -cost_to_depot)


        # --- CONSTRAINT FUNCTION 'Q' ---
        
        # Constraint 1: Each customer is visited exactly once.
        for j_cust_node in customer_nodes:
            variables = []
            for m in range(num_vehicles):
                # Ensure k goes up to the vehicle's specific limit
                for k in range(1, vehicle_k_limits[m] + 1):
                    variables.append((m, j_cust_node, k))
            constraint_qubo.add_only_one_constraint(variables, 1.0)

        # Constraint 2: Each vehicle is in AT MOST one place at a given time.
        for m in range(num_vehicles):
            k_max = vehicle_k_limits[m]
            for k in range(1, k_max + 1):
                variables = [(m, j_cust_node, k) for j_cust_node in customer_nodes]
                constraint_qubo.add_at_most_one_constraint(variables, 1.0)


        # --- Combine C and Q into the final QUBO ---
        final_qubo = Qubo()
        # Add values from cost_qubo, scaled by A1
        for field, value in cost_qubo.get_dict().items():
            final_qubo.add(field, value * A1)
        # Add values from constraint_qubo, scaled by A2
        for field, value in constraint_qubo.get_dict().items():
            final_qubo.add(field, value * A2)
            
        return final_qubo