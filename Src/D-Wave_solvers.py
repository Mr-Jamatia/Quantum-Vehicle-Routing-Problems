from dwave.system import DWaveSampler, EmbeddingComposite, LeapHybridSampler
from dwave.samplers import SimulatedAnnealingSampler
from dimod import ExactSolver

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