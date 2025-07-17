# 🧭 Quantum Vehicle Routing Problems – <br> Contribution & Structure Guide

**Version:** 1.0  
**Last Updated:** July 16, 2025  
**Maintainers:** Dr. Raja Babu Jamatia, Pawet Gora



<br><br>
🚀 Purpose

This repository aims to advance Quantum approaches to solving various classes of Vehicle Routing Problems (VRP), including Capacitated VRP (CVRP), VRP with Time Windows (CVRPTW), and generic VRP using hybrid, quantum-inspired, and classical methods.

🧱 Repository Structure

Quantum-Vehicle-Routing-Problems/
│
├── data/                     # Datasets for benchmarking VRP variants
│   ├── CVRP/
│   ├── CVRPTW/
│   └── VRP/
│
├── variants/                 # Core logic by VRP type
│   ├── CVRP/
│   │   ├── solvers/          # Variant-specific solver implementations
│   │   │   ├── shared/       # Reusable logic only for CVRP
│   │   ├── problem.py
│   │   └── utils.py
│   ├── CVRPTW/
│   │   ├── solvers/
│   │   │   ├── shared/
│   │   ├── problem.py
│   │   └── utils.py
│   ├── VRP/
│   │   ├── solvers/
│   │   │   ├── shared/
│   │   ├── problem.py
│   │   └── utils.py
│
├── src/                      # Shared modules across all VRPs
│   ├── common/               # Interfaces, routing abstractions, DW helpers
│   ├── encoding/             # QUBO encoding utilities
│   ├── preprocessing/        # Data transformation/standardization
│   └── analysis/             # Metrics, visualization, comparison
│
├── notebooks/                # Jupyter notebooks for experimentation
├── results/                  # Output results, plots, reports
├── docs/                     # Project documentation (e.g., architecture, specs)
├── images/                   # Supporting visual assets
├── tests/                    # Unit & integration tests
├── README.md
├── CONTRIBUTING.md
├── environment.yml           # Conda environment specification
└── requirements.txt          # Pip-based dependency list
📜 Coding Standards

Language: Python 3.10+
Formatting: Follow PEP8
Linting: Use flake8, black, and isort
Docstrings: NumPy style
Tests: Write unit tests using pytest and include at least 80% coverage
Type Hinting: Enforced across the entire codebase
