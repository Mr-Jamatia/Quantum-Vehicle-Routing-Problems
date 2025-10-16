from abc import ABC, abstractclassmethod
from time import time
import pygsp

from QuantumLogistics import Route 

class CompositeRouteSolver(ABC):
    """
        Abstract class to solve logistics problem on routes
        This is the most general type of solver that only required a solveAlgorithm and extractSolution definiton. 
        SOLVE() SHOULD *NOT* BE OVERWRITTEN. Only overwrite solveAlgorithm() and extractSolution()
    """

    def __init__(self):
        raise NotImplementedError

    
    def solve(self,route:Route, config = None):
        """
            DO NOT OVERWRITE METHOD
        """
        self.config = config
        startTime = time()

        # check if graph must be coarsened
        if route.coarsen:
            print("Coarsening Graph now")
            route.coarsenGraph()

        #TODO: Sometimes the solver may not find a feasible solution in the timelimit
        # Need to develop an exception handling method for this
        print("--- Debugging CompositeRouteSolver.solve ---")
        problemSol = self.solveAlgorithm(route)
        print(f"problemSol from solveAlgorithm: {problemSol}")

        routeSol = self.extractSolution(problemSol)
        print(f"routeSol from extractSolution: {routeSol}")

        #route.visualiseSolution(routeSol)
        
        if route.coarsen:
            routeSol = route.inflateGraph(routeSol)
            route.graph = route.originalGraph

        #route.visualiseSolution(routeSol)
    
        # Standard solver details
        solveTime = time() - startTime
        costValue = route.calculateCost(routeSol)

        return routeSol, solveTime, costValue


    @abstractclassmethod
    def solveAlgorithm(self, route: Route):
        """
            Returns raw output from solver in terms of decision variables.
            This should only include logic to SOLVE the problem (it should NOT DECODE the solution - this happens in extractSolution)

            Input:
                route: Route object

            Output:
                problem solution: solver dependant 
                    The output from the solver API/interface (not converted to route form)

        """

        raise NotImplementedError

    @abstractclassmethod
    def extractSolution(self, problemSol):
        """
            Decodes the solution from solver output to a standard route list for plotting and analysis.

            Input:
                problem solution: solver dependant 

            Output:
                Standard solution List - a list of vehicle routes where each route is a list of edges the vehicle travels (eadges in tuple format) 
            
                    i.e routeSol =  [[(idxDepot, idx1), (idx1, idx4), (idx4, idx5), (idx5, idxDepot)],                  # Vehicle 1 route
                                    [(idxDepot, idx2), (idx2, idx3), (idx3, idxDepot)],                                 # vehicle 2 route
                                    [(idxDepot, idx9), (idx9, idx8), (idx8, idx7), (idx7, idx6), (idx6, idxDepot)]]     # vehicle 3 route

        """
        raise NotImplementedError










class StandardRouteSolver(CompositeRouteSolver):

    def __init__(self, encoder, solver):
        self.encoder = encoder
        self.solver = solver
        return

    def solveAlgorithm(self, route:Route):
        #Encode problem
        problem = self.encoder.encode(route)

        #solving problem
        problemSol = self.solver.solve(problem, config = self.config)

        return problemSol


    def extractSolution(self,solverSolution):
        # must return standard solution
        return self.encoder.extract(solverSolution, verbose=False)






