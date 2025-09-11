from setuptools import find_packages, setup

setup(
    name="QuantumLogistics",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "matplotlib",
        "numpy",
        "cplex",
        "pygsp",
        "networkx",
        "qiskit",
        "qiskit_optimization",
        "dwave-ocean-sdk",
        "pulp",
        "pytest",
        "pandas",
        "graph_coarsening @ git+https://github.com/loukasa/graph-coarsening",
    ],
)
