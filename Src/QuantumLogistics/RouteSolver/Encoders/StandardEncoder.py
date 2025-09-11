from abc import ABC, abstractclassmethod, abstractmethod
from QuantumLogistics import Route # solver #, Encoder, solver



class Encoder(ABC):

    def __init__(self):
        """
            The encoder serves as the interface between the route and solver backend objects.

            The encoder converts the CVRP problem in the route object to a mathematical representation for solving byt the solver backend
            After solving, the encoder then extracts the information from the solver output and converts it to a route solution list
        """

        return

    @abstractmethod
    def encode(self,route: Route):
        """
            This encodes the cvrp problem in the route object into a problem be solved by a solver API

            Input:
                route - route object

            Output:
                solver api dependant
        
        """

        # to remember the route characteristics
        self.route = route

        # Must be output to a standard problem format
        raise NotImplementedError

    @abstractmethod
    def extract(self,solution) -> list:

        """ 
            This extracts the route solution from the solution given by the solver backend

            Input:
                problemSolution - solver dependant

            Output:
                Standard solution List - a list of vehicle routes where each route is a list of edges the vehicle travels (eadges in tuple format) 

                    i.e routeSol =  [[(idxDepot, idx1), (idx1, idx4), (idx4, idx5), (idx5, idxDepot)],                  # Vehicle 1 route
                                    [(idxDepot, idx2), (idx2, idx3), (idx3, idxDepot)],                                 # vehicle 2 route
                                    [(idxDepot, idx9), (idx9, idx8), (idx8, idx7), (idx7, idx6), (idx6, idxDepot)]]     # vehicle 3 route
        """

        raise NotImplementedError

    
    def addTWConstraints(self):

        """
            Not yet implemented - maybe coming soon
        """

        raise NotImplementedError
