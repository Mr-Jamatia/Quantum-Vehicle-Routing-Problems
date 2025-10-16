import numpy as np
from time import time
import csv


from QuantumLogistics import logisticsGraph, Route, StandardRouteSolver, ILPPulpEncoder, GurobiSolver, CBCSolver, DeltaCoarseningEngine, CompositeRouteSolver, GurobiSolver2
    
#################################################
#################################################
# GO TO THE BOTTOM OF THE FILE TO PUT YOUR CODE IN
#################################################
#################################################

def solveRoutingProblem(testSolver: CompositeRouteSolver, testSolverConfig: dict, numberTrucks = 2, numberOfNodes = 15, coarseningRate = 0.5, sampleSize = 20, verbose = False):
    """
        Example run file to test Quantum Optimisation Algorithm on the Vehicle Routing Problem
    """
    ############################################################################################################################
    # 1. Graph Definition
    ############################################################################################################################
    # This defines the primary features of the graph to be studied
    #   This is in the CVRP problem - with 'node demand'. Leave at 0.1 for general work
    graphType = "fully_connected"
    singleNodeCapacity = 0.1
    nodeCapacityDefinition = numberOfNodes * [singleNodeCapacity]  # A list of nodes 

    #+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+
    ############################################################################################################################
    # 2. Route Object Definiton
    ############################################################################################################################
    # This defines the operating details for the route (i.e number of trucks, truck capacity (how many nodes can a truck go to))
    #   For even distribution of trucks set routeConfig['truckCapacity'] == -1
    routeConfig = {     'vehicles' : numberTrucks,
                        'depot' : 0, 
                        'truckCapacity': -1}  # Set to -1 for auto (will evenly distribute trucks)

    ## Modifying truck capacity if set to auto
    if routeConfig['truckCapacity'] == -1:        
        Q = singleNodeCapacity * np.ceil((numberOfNodes+1) / routeConfig['vehicles'])
        routeConfig['truckCapacity'] = Q

    # Define Coarsening Object/methods 
    # This is if coarsening is set to true (i.e the optimiser coarsens the graph before solving)
    coarsenConfig = {'coarsenRate' : coarseningRate,
                     'radiusCoefficient': 0.2}

    coarseningEngine = DeltaCoarseningEngine(**coarsenConfig)

    #+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+
    ############################################################################################################################
    # 3. Solver Definiton 
    ############################################################################################################################

    # Define solver - using ILP encoder with CBC Solver for example
    solver = testSolver
    solverConfig = testSolverConfig

    #+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+
    ############################################################################################################################
    # 4. Solving
    ############################################################################################################################

    # statistical analysis
    numberofGraphSamples = sampleSize

    #generate a list of seeds used in run (for future reference)
    #np.savetxt("seedFiles.txt",np.random.randint(50000, size = numberofGraphSamples))

    #Loading Seeds
    seeds = np.loadtxt("seedFiles.txt").astype(np.int32)

    #numberofGraphSamples = len(seeds)

    SolutionList = []

    for runNumber in range(numberofGraphSamples):
        print("FOR RUN NUMBER :", runNumber)

        #Define the network object
        LogisticsNetwork = logisticsGraph(nodeCapacityDefinition, seed = seeds[runNumber], graph_type = graphType)
        LogisticsNetwork.generate_graph()

        # Plotting the network
        if verbose == True:
            LogisticsNetwork.plotGraph()

        #Create the route object
        route = Route(LogisticsNetwork, coarseningEngine = coarseningEngine, **routeConfig)

        # indicates coarsening is required
        route.coarsen = False 
        if coarseningRate < 1:
            route.coarsen = True

        # Solving Network
        solvedCoarseRoute, coarseSolveTime, coarseCost = solver.solve(route, config = solverConfig)
        coarseMIPGap = 0

        # Saving images
        rootFilePath = str(numberOfNodes) + '_' + str(numberTrucks) + '_' + str(coarsenConfig['coarsenRate']) + '_' + str(runNumber) + "saveImage.png"
        fineFilePath = "fine_" + rootFilePath
        coarseFilePath = rootFilePath
        #route.visualiseSolution(solvedFineRoute, saveImgFilepath=fineFilePath)
        route.visualiseSolution(solvedCoarseRoute, saveImgFilepath=coarseFilePath)
        #print(solvedCoarseRoute)
        #route.visualiseSolution(solvedCoarseRoute)

        #Output
        solutionList = [numberOfNodes, numberTrucks, coarsenConfig['coarsenRate'], runNumber, coarseCost, coarseSolveTime, coarseCost, coarseSolveTime]

        # Resetting csv File
        print("to csv")
        with open("csvOutputFile.csv", "a", newline = '') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerow(solutionList)

    return SolutionList



if __name__ == "__main__":

    # General Problem Details:
    numberOfNodes = 15
    numberTrucks = 1

    plotOutputs = False

    # The classical baseline solver: Known to give optimal results through an ILP formulation
    # solver = StandardRouteSolver(ILPPulpEncoder(), GurobiSolver())
    solver = StandardRouteSolver(ILPPulpEncoder(), CBCSolver())
    #solver = StandardRouteSolver(ILPPulpEncoder(), GurobiSolver2())

    solverConfig = {"testVar": 1,
                    "gapRel" : 0.005,
                    "timeLimit" : 600}

    sampleSize = 20

    graphSizes = [80, 120, 160] #Tested 20, 30, 50, 60
    coarseningRates = [1,0.9,0.7,0.5,0.3] #[1,0.9,0.7,0.5,0.3]

    # Resetting csv File
    with open("csvOutputFile.csv", "w", newline = '') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow([0])

    for size in graphSizes:
        for coarseningRate in coarseningRates:
            inputVect = {   "numberOfNodes" : size,
                            "numberTrucks": numberTrucks,
                            "coarseningRate": coarseningRate, 
                            "sampleSize": sampleSize, 
                            "verbose" : plotOutputs, }

            # solve Problem: (30 optimisation runs)
            print("Testing with coarsening Rate ", coarseningRate)
            print("Testing with size: ", size)

            solutionList = solveRoutingProblem(solver, solverConfig, **inputVect)
            print(solutionList)
    
        # Need to start from Run 12, 50 nodes, 0.5 coarsening
        
        
        
    