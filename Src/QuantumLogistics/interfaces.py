
from abc import ABC, abstractclassmethod
from matplotlib.colors import ListedColormap
from pygsp import graphs

class VRPGraph:
    def __init__(self, loadFromFile = False, fileName = None):

        if loadFromFile:
            self.loadGraphFromFile(fileName)
        else:
            self.generateGraph() # needs params etc

        self.coarse = False
        
        return


    def setSeed(self, seed=None):

        raise NotImplementedError


    def generateGraph(self) -> graphs.Graph:
        self.graph = None

        raise NotImplementedError

    
    def loadGraphFromFile(self):

        raise NotImplementedError




    # required functions:
    #       Generate a graph instance (in networkx graph) (generate x,y points and put into graph)
    #       Set seed
    #       Coarsen graph for easier representation
    #       Uncoarsen graph





class VRPRoute:
    """
        Should include capacity and demand
    """
    def __init__(self, graph, config):

        self.status = {'solved':False}

        return



    def visualiseRoute(self, VRPSolution):

        raise NotImplementedError



    def evaluateKPIs(self):


        raise NotImplementedError


    def recordMetaData(self):
        """
            Add important details to self.metaData for later analysis
        """
        raise NotImplementedError


    def coarsenGraph(self, coarsenConfig, coarsenAlg = None):
        """
            Coarsen a provided graph to generate a compressed representation
        """
        coarseGraph = None
        coarsenConfig = coarsenConfig

        raise NotImplementedError



    def inflateGraph(self, coarseGraph):
        """
            Is this needed?
        """
        raise NotImplementedError





class VRPSolver(ABC):

    "ABC with both a solver and model converter"

    
    # required functions:
    #       Solve the route problem
    #           Convert problem to a sufficient model
    #           Solve the problem using either quantum or classical (or both) methods
    #       Validate feasibility
    #       Extract data from solution


    def __init__(self, RouteEncoder):

        return


    @abstractclassmethod
    def solveVRP(self, VRPRoute: VRPRoute) -> list:
        """
            Needs the route instance
        """
        # converts to required format
        # solves
        # extracts data
        # validates feasibility
        # returns a k-long list of routes (one route for each vehicle)
        #[[1,2,5,6,1], [8,9,10,8]]



        return


    @abstractclassmethod
    def validateFeasibility(self):

        return


    @abstractclassmethod
    def extractData(self):

        return

    







class VRPVQESolver(VRPSolver):

    def __init__(self, RouteEncoder, ):

        return






class VRPQASolver(VRPSolver):

    def __init__(self, RouteEncoder, ):

        return






class VRPQAOASolver(VRPSolver):
    
    def __init__(self, RouteEncoder, ):

        return






class VRPClassicalSolver(VRPSolver):

    def __init__(self, RouteEncoder):

        return






class RouteEncoder(ABC):
    """ Converts to either a QUBO, ILP etc for solving"""

    def __init__(self, ):

        return

    @abstractclassmethod
    def encodeRoute():

        return



class QUBOEncoder(RouteEncoder):
    def __init__(self, ):

        return




class ILPEncoder(RouteEncoder):
    def __init__(self, ):

        return





class solver_backend():
    """Collection of solver functions for all interfaces - i.e gurobi, qiskit, dwave"""





# Definitions
# VRP Graph - collection of (x,y) points representing locations. Assumes all locations are fully connected
# Route - a sequence (or combination of sequences) travelled by a vehicle to reach all (x,y) points in route
# VRPSolver - an object which 

if __name__ == "__main__":

    # example of comparing multiple types of solvers

    # 1. generate graph object - loading in from a saved file
    graphFileName = 'experimentalGraph.csv'
    VRPnetwork = VRPGraph(loadFromeFile = True, filename = graphFileName)

    # 2. Define configuration for route:
    config = {  'vehicles' : 7,
                'depot' : 0,
                'capacity': -1,
                'demand': -1  }

    # 3. Define solvers to compare: (including all variations etc)
    solverList = [VRPClassicalSolver, VRPQAOASolver, VRPVQESolver, VRPQASolver]
    solutionList = []

    # 4. Iterate through solver list and solve for each tested
    for solver in solverList:
        # define route
        route = VRPRoute(VRPnetwork, config)
        
        #route.coarsenGraph()

        # solve route
        solvedRoute = solver.solve(route, solverConfig)
        
        # add solved route to list for post-processing
        solutionList.append(solvedRoute)

    # 5. Post Process - can also do it while solving stuff
    for solvedRoute in solutionList:
        results = solvedRoute.evaluateKPIs()



