import DWaveSolvers_modified
from vrp_solution import VRPSolution
import math

class VRPSolver:
    def __init__(self, problem):
        self.problem = problem

    def solve(self, A1, A2, solver_type, num_reads):
        pass

class FullQuboSolver(VRPSolver):
    def solve(self, A1, A2, solver_type='simulated', num_reads=50):
        num_customers = len(self.problem.dests)
        num_vehicles = len(self.problem.capacities)
        
        k_max = num_customers
        vehicle_k_limits = [k_max] * num_vehicles

        vrp_qubo = self.problem.get_qubo_paper(vehicle_k_limits, A1, A2)
        
        try:
            samples = DWaveSolvers_modified.solve_qubo(vrp_qubo, solver_type=solver_type, limit=1, num_reads=num_reads)
        except Exception as e:
            print(f"Solver error: {e}")
            return VRPSolution(self.problem, {}, vehicle_k_limits, solution=[])
        
        if not samples:
             return VRPSolution(self.problem, {}, vehicle_k_limits, solution=[])

        solution = VRPSolution(self.problem, samples[0], vehicle_k_limits)
        return solution

class AveragePartitionSolver(VRPSolver):
    def solve(self, A1, A2, solver_type='simulated', num_reads=50, limit_radius=1):
        num_customers = len(self.problem.dests)
        num_vehicles = len(self.problem.capacities)

        avg_per_vehicle = math.ceil(num_customers / num_vehicles)
        k_max = avg_per_vehicle + limit_radius
        vehicle_k_limits = [k_max] * num_vehicles

        vrp_qubo = self.problem.get_qubo_paper(vehicle_k_limits, A1, A2)

        try:
            samples = DWaveSolvers_modified.solve_qubo(vrp_qubo, solver_type=solver_type, limit=1, num_reads=num_reads)
        except Exception as e:
            print(f"Solver error: {e}")
            return VRPSolution(self.problem, {}, vehicle_k_limits, solution=[])

        if not samples:
             return VRPSolution(self.problem, {}, vehicle_k_limits, solution=[])

        solution = VRPSolution(self.problem, samples[0], vehicle_k_limits)
        return solution