
class VRPSolution:
    def __init__(self, problem, sample, vehicle_k_limits, solution=None):
        self.problem = problem
        
        if solution is not None:
            self.solution = solution
        else:
            num_vehicles = len(self.problem.capacities)
            temp_routes = {i: [] for i in range(num_vehicles)}

            for var, val in sample.items():
                if val == 1:
                    i, j, k = var
                    temp_routes[i].append((k, j))

            final_routes = []
            for i in range(num_vehicles):
                sorted_visits = sorted(temp_routes[i], key=lambda x: x[0])
                route = [j for k, j in sorted_visits]
                final_routes.append(route)
            
            self.solution = final_routes

    def check(self):
        
        # --- Check for duplicate visits ---
        all_visited_dests_list = [dest for route in self.solution for dest in route]
        
        # 1. Did we visit the correct number of locations?
        if len(all_visited_dests_list) != len(self.problem.dests):
            print(f"Warning: Incorrect number of total visits. Required: {len(self.problem.dests)}, Found: {len(all_visited_dests_list)}")
            return False
            
        # 2. Are there any duplicate visits across all routes?
        if len(set(all_visited_dests_list)) != len(all_visited_dests_list):
            print(f"Warning: Duplicate customer visits found in solution.")
            return False

        # 3. Capacity Check
        # --- NOTE FOR DEVELOPERS: POST-ANALYSIS CAPACITY CHECK ---
        # The FQS and APS solvers are for VRP and are "blind" to capacity.
        # This check is performed *after* the solver returns a result to see
        # if the VRP solution incidentally respects the capacity constraints.
        # A 'False' result from this check indicates that a true CVRP
        # solver is required for this problem instance.
        capacities = self.problem.capacities
        weights = self.problem.weights
        for i, route in enumerate(self.solution):
            vehicle_load = sum(weights[dest] for dest in route)
            if vehicle_load > capacities[i]:
                print(f"Warning: Vehicle {i} exceeds capacity. Load: {vehicle_load}, Capacity: {capacities[i]}")
                return False

        return True

    def total_cost(self):
        costs = self.problem.costs
        depot = self.problem.source_depot
        total_cost = 0

        for route in self.solution:
            if not route:
                continue
            
            current_cost = costs[depot][route[0]]
            for i in range(len(route) - 1):
                current_cost += costs[route[i]][route[i+1]]
            current_cost += costs[route[-1]][depot]
            
            total_cost += current_cost
            
        return total_cost

    def description(self):
        print("Solution Routes:")
        for i, route in enumerate(self.solution):
            if route:
                full_path = [self.problem.source_depot] + route + [self.problem.source_depot]
                print(f"  Vehicle {i}: {' -> '.join(map(str, full_path))}")
            else:
                print(f"  Vehicle {i}: Not used")
        print(f"\nTotal Cost: {self.total_cost():.2f}")
        print(f"Is Solution Valid: {self.check()}")

