import numpy as np
from time import time
import csv, os

from QuantumLogistics import logisticsGraph, Route, StandardRouteSolver, ILPPulpEncoder, GurobiSolver, CBCSolver \
    , DeltaCoarseningEngine, CompositeRouteSolver, GurobiSolver2
from QuantumLogistics.LogisticsRoute.VrpRepGraph import vrpRepGraph

#################################################
#################################################
# GO TO THE BOTTOM OF THE FILE TO PUT YOUR CODE IN
#################################################
#################################################

dataDir = os.path.join(os.getcwd(), "../../dataset")

csvSaveDir = "csvOutputFile.csv"

def solveRoutingProblem(testSolver: CompositeRouteSolver, testSolverConfig: dict, 
                        cmtFile = 'CMT11.xml', numberTrucks = 2, coarseningRate = 0.5, 
                        sampleSize = 1, CMTBKS = 1000, verbose = False):
    """
        Example run file to test Quantum Optimisation Algorithm on the Vehicle Routing Problem
    """
    ############################################################################################################################
    # 1. Graph Definition
    ############################################################################################################################
    root = dataDir
    file =  os.path.join(root, cmtFile)
    print(f'[i] Loading graph file {file}...')
    LogisticsNetwork = vrpRepGraph(file)
    LogisticsNetwork.generate_graph()

    print(f'[i] Setting graph configurations for {file}...')    
    numberOfNodes = LogisticsNetwork.n
    print(f'[i] Number of nodes {numberOfNodes} ...')    
    
    truckCapacity = max(LogisticsNetwork.nodeCapacities)
    print(f'[i] Truck Capacity {truckCapacity} ...')    
    
    depot = LogisticsNetwork.nodelist.vehicle['arrival_node']
    print(f'[i] Depot Node {depot} ...')    

    #+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+#+
    ############################################################################################################################
    # 2. Route Object Definiton
    ############################################################################################################################
    # This defines the operating details for the route (i.e number of trucks, truck capacity (how many nodes can a truck go to))
    routeConfig = {     'vehicles' : numberTrucks,
                        'depot' : depot, 
                        'truckCapacity': truckCapacity}  # Set to -1 for auto (will evenly distribute trucks)

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

    allSolutionsList = []
    for runNumber in range(numberofGraphSamples):
        print("FOR RUN NUMBER :", runNumber)
        LogisticsNetwork = vrpRepGraph(file)
        LogisticsNetwork.generate_graph()

        # Plotting the network
        if verbose:
            LogisticsNetwork.plotGraph()

        # Create the route object
        route = Route(LogisticsNetwork, coarseningEngine = coarseningEngine, **routeConfig)

        # Indicates coarsening is required
        route.coarsen = False 
        if coarseningRate < 1:
            route.coarsen = True

        # Solving Network
        #try: Sometimes the solver won't find a solution and causes an error. 
        solvedRoute, solveTime, cost = solver.solve(route, config = solverConfig)
        # Saving images
        savefilePath = cmtFile + '_' + str(coarsenConfig['coarsenRate']) + '_' + str(runNumber) + "saveImage.png"
        route.visualiseSolution(solvedRoute, saveImgFilepath=savefilePath)
        #except:
            # print("No Solution Found in time limit")
            # cost = 0
            # solveTime = 'Not Solved'
            
        #Output
        solutionList = [cmtFile, numberTrucks, coarsenConfig['coarsenRate'], runNumber, cost, cost/CMTBKS, solveTime]

        with open(csvSaveDir, "a", newline="") as csv_file:
            writer = csv.writer(csv_file, delimiter=",")
            writer.writerow(solutionList)

        allSolutionsList.append(solutionList)

    return allSolutionsList



if __name__ == "__main__":
    # General CMT Details: {cmt numer : (number Trucks, optimal value)} 
    # http://vrp.atd-lab.inf.puc-rio.br/index.php/en/
    CMTDetails = {'01' : (5,    524.61) ,
                  '02' : (10,   835.26) ,
                  '03' : (8,    826.14) ,
                  '04' : (12,   1028.42),
                  '05' : (17,   1291.29),
                  '11' : (7,    1042.12),
                  '12' : (10,   819.56) }
                  # These instances are made with time windows and cannot be solved
                  # with the current solver method
                  #'06' : (6,    555.43) ,
                  #'07' : (11,   909.68) ,
                  #'08' : (9,    865.94) ,
                  #'09' : (14,   1162.55),
                  #'10' : (18,   1395.85),
                  #'13' : (11,   1541.14),
                  #'14' : (11,   866.37) }
    
    # General Problem Details:
    plotOutputs = False

    # SOLVER AND ENCODER DEFINITION
    encoder = ILPPulpEncoder()

    # The classical baseline solver: Known to give optimal results through an ILP formulation
    solverAlg = CBCSolver()
    #solver = GurobiSolver()

    solver = StandardRouteSolver(encoder, solverAlg)
    solverConfig = {"testVar": 1,
                    "gapRel" : 0.005,
                    "timeLimit" : 300}
    
    #General Experiment Settings
    sampleSize = 1
    coarseningRates = [1,0.9,0.7,0.5,0.3] 

    # Resetting csv File
    with open(csvSaveDir, "w", newline = '') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(["cmtFileName", "Number of Trucks", "Coarsening Rate", "Run Number", "Solution Cost", "Relative Cost", "Solve Time"])

    for cmtNum, cmtData in CMTDetails.items():
        truckNumber = cmtData[0]
        cmtfile = "CMT" + cmtNum + '.xml'
        
        for coarseningRate in coarseningRates:
            print("Testing with coarsening Rate ", coarseningRate)

            inputVect = {   "cmtFile" : cmtfile,
                            "numberTrucks": truckNumber,
                            "CMTBKS" : cmtData[1],
                            "coarseningRate": coarseningRate, 
                            "sampleSize": sampleSize, 
                            "verbose" : plotOutputs, }

            solutionList = solveRoutingProblem(solver, solverConfig, **inputVect)
            print(solutionList)
