from abc import ABC, abstractclassmethod
import pulp as pl
import numpy as np
import cplex
import pandas as pd
import sys

# dirty hack, I am aware
# sys.path.insert(0, "/home/knalecz/Pulpit/PhD/aktualne_projekty/QReaserch/VRP-explorations")

# from VRP.quantum.BQM_based.full_qubo_solver import CapcFullQuboSolver as CFQS


class Solver(ABC):
    def __init__(self):

        return

    @abstractclassmethod
    def solve(self, problemFormat, config):
        """
            This accepts a standardised problemFormat datatype (dependant on encoder) and runs the problem using a specified solver backend.

            This format should be as general as possible to cater to a wide range of solvers. 

            For example:
                ILP problems accepts a PULP problem which encodes the ILP problem
                Standard qubo problems will likely accept a standard 'QUBO' format that can be readily converted into DWAVE, QISKIT etc solver format.

        """

        raise NotImplementedError


class PulpSolver(Solver):
    def __init__(self):
        return

    def defineSolver(self):
        """
        """
        raise NotImplementedError("Use either Gurobi or CBC solvers")

    def solve(self, problem: pl.LpProblem, config=None):
        # Define the solver - defaults if no config specified
        if config:
            gap_rel = config.get("gapRel", 0.01)
            timeLimit = config.get("timeLimit", 300)
        else:
            gap_rel = 0.01
            timeLimit = 300
            print(
                f"No config specified, defaulting to gap_rel = {gap_rel} and timeLimit {timeLimit}"
            )

        self.solver = self.defineSolver(gap_rel=gap_rel, time_lim=timeLimit)

        prob = problem
        solver = self.solver
        prob.solve(solver)

        print(f'"Status:", {pl.LpStatus[prob.status]}')

        if prob.status == 0:
            print(
                f"Not possible to find a solution with the tolerance {gap_rel} in {timeLimit}s"
            )
            return

        elif prob.status == 1:
            obj = pl.value(prob.objective)
            print(f"The Objective function Value is: {round(obj,3)}")

            solution = []
            solution_name = []

            for v in prob.variables():
                value = round(v.varValue, 4)
                if v.isInteger():
                    value = round(v.varValue)
                solution.append(value)
                solution_name.append(v.name)

            # map the pulp solution format to matchs with CPLEX
            temp = [
                (ii, jj, int(jj.split("_")[1]))
                for ii, jj in zip(solution, solution_name)
            ]
            df = pd.DataFrame(temp, columns=["Value", "Name", "position"])
            df = df.sort_values(by="position")
            x = df.Value.values
            solution_name = df.Name.values
            return x

        else:
            print("Problem is infeasible")
            return

    def verifyConstraints(self, prob):

        soln_dict = {i.name: round(i.varValue, 1) for i in prob.variables()}

        for c in prob.constraints.values():
            c_dict = c.toDict()
            # print(c_dict)
            satisfied = False

            LHS = sum(
                [soln_dict[i["name"]] * i["value"] for i in c_dict["coefficients"]]
            )
            LHS = LHS + c_dict["constant"]

            if c_dict["sense"] == 0:
                satisfied = LHS == 0

            if c_dict["sense"] == -1:
                satisfied = LHS <= 0

            if c_dict["sense"] == 1:
                satisfied = LHS >= 0

            if not satisfied:
                # print('LHS: ', LHS)
                print(c)
                print("not satisfied")

        return


class GurobiSolver(PulpSolver):
    def defineSolver(self, gap_rel, time_lim):
        return pl.GUROBI_CMD(msg=1, gapRel=gap_rel, timeLimit=time_lim)


class GurobiSolver2(PulpSolver):
    def defineSolver(self, gap_rel, time_lim):
        return pl.GUROBI(msg=1, gapRel=gap_rel, timeLimit=time_lim)


class CBCSolver(PulpSolver):
    def defineSolver(self, gap_rel, time_lim):
        return pl.PULP_CBC_CMD(msg=1, gapRel=gap_rel, timeLimit=time_lim)


class CPLEXSolver(PulpSolver):
    def defineSolver(self, gap_rel, time_lim):
        return pl.CPLEX_PY(msg=1, gapRel=gap_rel, timeLimit=time_lim)


class CPLEXNativeSolver(Solver):
    def __init__(self):

        return

    def solve(self, my_prob: cplex.Cplex):

        try:
            my_prob.solve()
        except cplex.CplexError as exc:
            print(exc)
            return

        x = my_prob.solution.get_values()
        x = np.array(x)
        cost = my_prob.solution.get_objective_value()

        # needs a consistent return -
        return x


class VRPExplorationsSolver(Solver):

    def solve(self, problemFormat, config):
        # przykład wykorzystania CapcSolutionPartitionSolver → https://github.com/AsishMandoi/VRP-explorations/blob/main/VRP/quantum/BQM_based/Vehicle%20Routing%20Problem.ipynb
        self.vrp_explorations_solver = CFQS(
            problemFormat.clients_num - 1,
            problemFormat.vehicles_num,
            problemFormat.cost_matrix,
            [problemFormat.capacity]*problemFormat.vehicles_num,
            problemFormat.demands
        )
        self.vrp_explorations_solver.solve(solver=config['solver'])

        # self.vrp_explorations_solver.solution → efekt wywołania metody VehicleRouter#extract_solution
        return self.vrp_explorations_solver.solution
