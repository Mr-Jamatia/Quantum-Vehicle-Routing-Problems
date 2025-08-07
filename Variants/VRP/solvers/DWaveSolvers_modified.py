# from dwave.system.samplers import DWaveSampler
# from dwave.system.composites import EmbeddingComposite
# from hybrid.reference.kerberos import KerberosSampler
# from dimod.reference.samplers import ExactSolver
# import hybrid
# import dimod
# import neal  # This is the classical solver we are using

from dwave.system import DWaveSampler, EmbeddingComposite, LeapHybridSampler
from dwave.samplers import SimulatedAnnealingSampler
from dimod import ExactSolver


# # Creates hybrid solver.
# def hybrid_solver():
#     workflow = hybrid.Loop(
#         hybrid.RacingBranches(
#         hybrid.InterruptableTabuSampler(),
#         hybrid.EnergyImpactDecomposer(size=30, rolling=True, rolling_history=0.75)
#         | hybrid.QPUSubproblemAutoEmbeddingSampler()
#         | hybrid.SplatComposer()) | hybrid.ArgMin(), convergence=1)
#     return hybrid.HybridSampler(workflow)

# def get_solver(solver_type):
#     solver = None
#     if solver_type == 'standard':
#         solver = EmbeddingComposite(DWaveSampler())
#     if solver_type == 'hybrid':
#         solver = hybrid_solver()
#     if solver_type == 'kerberos':
#         solver = KerberosSampler()
#     # The 'qbsolv' block is REMOVED
#     if solver_type == 'exact':
#         solver = ExactSolver()
#     if solver_type == 'simulated':
#         solver = neal.SimulatedAnnealingSampler()
#     return solver

def get_solver(solver_type):
    """
    Returns appropriate solver based on type.
    Uses latest D-Wave Ocean SDK components.
    """
    if solver_type == 'qpu':
        return EmbeddingComposite(DWaveSampler())
    elif solver_type == 'hybrid':
        return LeapHybridSampler()
    elif solver_type == 'simulated':
        return SimulatedAnnealingSampler()
    elif solver_type == 'exact':
        return ExactSolver()
    else:
        raise ValueError(f"Solver type '{solver_type}' is not supported.")
    

# def solve_qubo(qubo, solver_type = 'simulated', limit = 1, num_reads = 50):
#     sampler = get_solver(solver_type)
#
#     if sampler is None:
#         raise ValueError(f"Solver type '{solver_type}' is not recognized or has been removed.")
#
#     # The logic is now much simpler and does not reference QBSolv
#     response = sampler.sample_qubo(qubo.dict, num_reads=num_reads)
#
#     # we use .lowest() to get the best results from the sampler
#     return list(response.lowest())[:limit]

def solve_qubo(qubo, solver_type='simulated', limit=1, num_reads=50):
    """
    Solve QUBO using specified solver type.
    Updated for latest Ocean SDK.
    """
    sampler = get_solver(solver_type)
    
    # Handle different solver types appropriately
    if solver_type == 'hybrid':
        # Hybrid solver doesn't use num_reads parameter
        response = sampler.sample_qubo(qubo.dict)
    elif solver_type == 'exact':
        # Exact solver doesn't use num_reads parameter
        response = sampler.sample_qubo(qubo.dict)
    else:
        # QPU and simulated annealing use num_reads
        response = sampler.sample_qubo(qubo.dict, num_reads=num_reads)
    return [sample for sample in response.lowest()][:limit]