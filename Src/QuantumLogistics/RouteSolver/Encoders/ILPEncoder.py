import numpy as np
import pandas as pd
import math
import pulp as pl
import cplex

#Custom Imports
from QuantumLogistics import Route
from .StandardEncoder import Encoder


class ILPPulpEncoder(Encoder):
    """
        Converts VRP problem into a PuLP ILP problem.
        This is used for classical solvers.
    """
    def __init__(self):

        return


    def encode(self, route:Route) -> pl.LpProblem:
        """
            Uses pulp to return the definition of ILP problem
            This is based on the Miller Tucker Zemlin formulation of the CVRP problem of an n node graph
            Decision Vars: 
                dec_x - whether to travel on edge ij [size nxn]
                dec_u - the 'integral' variable indicating the 'used truck capacity' of the truck at that node
        """
        print("Starting problem encoding")

        # to remember the route characteristics
        self.route = route
        n = route.graph.N
        K = route.vehicles
        graphAdjMatr = route.graph.W.toarray() 

        # Capacities:
        nodeCapacities = route.nodeCapacities
        Q = self.route.truckCapacity

        # Start the LP problem definition
        prob = pl.LpProblem("VRP", pl.LpMinimize)

        # define the decision variable
        dec_x = list(range(n ** 2))
        dec_u = list(range(dec_x[-1] + 1, dec_x[-1] + n))
        dec_total = dec_x + dec_u

        var_x = pl.LpVariable.dicts("x", dec_x, 0, 1, cat='Integer')
        var_u = pl.LpVariable.dicts("u", dec_u, min(nodeCapacities), Q, cat="Continuous")

        # merge both dictionaries
        l = [var_x, var_u]
        dec_vars = {**l[0], **l[1]}
        
        # create the dictonary for the weights:
        my_obj = list(graphAdjMatr.reshape(1, n ** 2)[0]) + [0.0 for x in range(0, n - 1)]
        weight_opt = dict(zip(dec_vars, my_obj))

        # Define the Objective function
        prob += pl.lpSum([weight_opt[i]*dec_vars[i] for i in dec_total])
        
        # create the array with all the right hand size contrainst values
        # This is the order in which constraints are made
        # first line - sum of xijk for each node (depot is idx 0 ) must be either # vehicles or 1. Multipled by 2 for entry and exit
        # second line - ui values are less than truck capacity
        # third line - paths from node to node i (self paths) must not be selected

        # subject to the node-visiting and the depot-visiting constraints:
        # MASS CONSERVATION CONSTRAINTS:
        entryExitConstraints = [K] + [1 for x in range(0, n - 1)]
        for ii in range(0, n):
            # Summing by row - all exits must equal 1 (or # of vehicles for depot)
            col = [x for x in range(0 + n * ii, n + n * ii)]
            constraint = entryExitConstraints[ii]
            prob += pl.lpSum([dec_vars[k] for k in col]) == constraint

        for ii in range(0, n):
            # Summing by row - all entries must equal 1 (or # of vehicles for depot)
            col = [x for x in range(0 + ii, n ** 2, n)]
            constraint = entryExitConstraints[ii]
            prob += pl.lpSum([dec_vars[k] for k in col]) == constraint

        # Sub-tour elimination constraints through capacities:
        for ii in range(0, n):
            for jj in range(0, n):
                # NOTE : Sub-Tour Elimination
                if (ii != jj) and (ii * jj > 0): # if i or j not 0
                    col = [ii + (jj * n), n ** 2 + ii - 1, n ** 2 + jj - 1]
                    coef = [Q, 1, -1]
                    capDeltaConstraint = Q - nodeCapacities[jj]
                    prob += pl.lpSum([co*dec_vars[k] for co, k in zip(coef,col)]) <= capDeltaConstraint

        # setting decision variable associated with 0 elements in adjacency to 0:
        zeroEdges = np.argwhere(graphAdjMatr == 0)
        for entry in zeroEdges:
            prob += pl.lpSum([dec_vars[entry[0] + (entry[1] * n)]]) == 0

        # # This also includes - set the diagonal elements to zero , i=j
        # for ii in range(0, n):
        #     col = [(ii) * (n + 1)]
        #     prob += pl.lpSum([dec_vars[k] for k in col]) == 0

        return prob


    def addCapacityConstraints(self):
        raise NotImplementedError

    def addTWConstraints(self):
        raise NotImplementedError


    def extract(self, solution, verbose = True):
        """
            Returns the route lists from the PULP ILP in the correct format
            Format is: 

        """
        # convert to route solution format
        #route information
        n = self.route.graph.N
        _k = n*n
        depotIdx = self.route.depot
        vehicleNumber = self.route.vehicles

        # After solving the Linear Program, it is needed to extract the routes from the solution
        routes = []
        _chain = []

        travel_metrices = solution[0:_k].reshape((n, n))

        for ix in range(0, n):
            for iy in range(0, n):
                if travel_metrices[ix][iy] > 0:
                    if (ix, iy) not in _chain and ix != iy:
                        _chain += [(ix, iy)]


        #self.route.visualiseSolution([_chain])

        for vehicle in range(vehicleNumber):
            cur = depotIdx
            route = []
            travel = True
            if verbose: print(f"{cur}", end='  ')
            counter = 0
            while travel:
                counter+= 1

                element = [(_from, _to) for (_from, _to) in _chain if _from == cur]
                (_from, _to) = element[vehicle] if len(element) > 1 else element[0]
                cur = _to
                if (_from, _to) in route:
                    print("There is a repeating cycle")
                    print((_from, _to))
                    self.route.visualiseSolution([route])
                    print(ThisWillErrorThingsOut)
                    break
                route += [(_from, _to)]
                if verbose: print(f"->  {_to}", end='  ')

                if cur == depotIdx:
                    travel = False
                #print(route)
            routes += [route]
            if verbose: print()

        # Check if all vehicles are accounted for, while calcultaing the routes
        assert len(routes) == vehicleNumber

        return routes





class ILPCPLEXEncoder(ILPPulpEncoder):
    """
        Converts the route into an ILP problem
        Inherits the extract() method from the ILPPulpEncoder Class (they have equivalent answers)
        THIS NEEDS TO BE UPDATED
    """

    def encode(self,route) -> cplex.Cplex:
        # to remember the route characteristics
        self.route = route
        n = route.n
        K = route.vehicles
        graphAdjMatr = route.graph.W.toarray() 

        Q = 10
        
        my_obj = list(graphAdjMatr.reshape(1, n ** 2)[0]) + [0.0 for x in range(0, n - 1)]
        my_ub = [1 for x in range(0, n ** 2 + n - 1)]
        my_lb = [0 for x in range(0, n ** 2)] + [0.1 for x in range(0, n - 1)]
        my_ctype = "".join(["I" for x in range(0, n ** 2)]) + "".join(
            ["C" for x in range(0, n - 1)]
        )

        my_rhs = (
            2 * ([K] + [1 for x in range(0, n - 1)])
            + [Q - 0.1 for x in range(0, (n - 1) ** 2 - (n - 1))]
            + [0 for x in range(0, n)]
        )
        my_sense = (
            "".join(["E" for x in range(0, 2 * n)])
            + "".join(["L" for x in range(0, (n - 1) ** 2 - (n - 1))])
            + "".join(["E" for x in range(0, n)])
        )

        try:
            my_prob = cplex.Cplex()
            self.populatebyrow(my_prob, my_obj, my_ub, my_lb, my_ctype, my_sense, my_rhs)
        except cplex.CplexError as exc:
            print(exc)
            return

        return my_prob


    def populatebyrow(self, prob, my_obj, my_ub, my_lb, my_ctype, my_sense, my_rhs):

        Q = 10 #THIS NEEDS TO BE PROVED AND INTEGRATED BETTER

        n = self.route.n

        prob.objective.set_sense(prob.objective.sense.minimize)
        prob.variables.add(obj=my_obj, lb=my_lb, ub=my_ub, types=my_ctype)

        prob.set_log_stream(None)
        prob.set_error_stream(None)
        prob.set_warning_stream(None)
        prob.set_results_stream(None)

        rows = []
        for ii in range(0, n):
            col = [x for x in range(0 + n * ii, n + n * ii)]
            coef = [1 for x in range(0, n)]
            rows.append([col, coef])

        for ii in range(0, n):
            col = [x for x in range(0 + ii, n ** 2, n)]
            coef = [1 for x in range(0, n)]

            rows.append([col, coef])

        # Sub-tour elimination constraints:
        for ii in range(0, n):
            for jj in range(0, n):
                if (ii != jj) and (ii * jj > 0):

                    col = [ii + (jj * n), n ** 2 + ii - 1, n ** 2 + jj - 1]
                    coef = [Q, 1, -1]

                    rows.append([col, coef])

        for ii in range(0, n):
            col = [(ii) * (n + 1)]
            coef = [1]
            rows.append([col, coef])

        prob.linear_constraints.add(lin_expr=rows, senses=my_sense, rhs=my_rhs)







