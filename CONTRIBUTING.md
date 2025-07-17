# 🧭 Quantum Vehicle Routing Problems – <br> Contribution & Structure Guide <br>


**Version:** 1.0  
**Last Updated:** July 17, 2025  
**Maintainers:** Dr. Raja Babu Jamatia, Dr. Pawet Gora


---

## 🚀 Purpose

This repository aims to advance **Quantum and Hybrid Approaches** for solving a wide range of Vehicle Routing Problems (VRP), including:

- Capacitated VRP (CVRP)
- VRP with Time Windows (CVRPTW)
- General VRP Models

It encourages development using **Quantum-Inspired**, **Hybrid Quantum-Classical**, and **Classical AI/OR** methods.

---




## 🧱 Repository Structure

```bash
Quantum-Vehicle-Routing-Problems/
│
├── data/                                # Centralized input datasets
│   ├── CVRP/
│   ├── CVRPTW/
│   └── VRP/
│
├── variants/                            # Core logic grouped by VRP variants
│   ├── CVRP/
│   │   ├── solvers/
│   │   │   ├── __init__.py
│   │   │   ├── greedy_solver.py
│   │   │   ├── hybrid_solver.py
│   │   │   ├── qubo_dwave_solver.py
│   │   │   └── shared/                 # Shared logic local to CVRP solvers
│   │   │       ├── unconstrained_qubo.py
│   │   │       └── penalty_utils.py
│   │   ├── problem.py
│   │   └── utils.py
│   │
│   ├── CVRPTW/
│   │   ├── solvers/
│   │   │   ├── hybrid_solver.py
│   │   │   ├── qubo_dwave_solver.py
│   │   │   ├── tabu_solver.py
│   │   │   └── shared/                # Shared logic local to CVRPTW solvers
│   │   │       └── time_window_encoding.py
│   │   ├── problem.py
│   │   └── utils.py
│   │
│   ├── VRP/
│   │   ├── solvers/
│   │   │   ├── baseline_solver.py
│   │   │   ├── qubo_classical_emulation.py
│   │   │   └── shared/               # Placeholder if reusable components emerge
│   │   ├── problem.py
│   │   └── utils.py
│
├── src/                                 # Shared core modules across all variants
│   ├── common/                          # Generic interfaces, models, helpers
│   │   ├── routing_problem.py
│   │   ├── routing_solution.py
│   │   └── dwave_helper.py
│   ├── encoding/
│   ├── preprocessing/
│   └── analysis/
│
├── notebooks/                           # Jupyter notebooks for experimentation
├── results/                             # Output results, graphs, logs
├── tests/                               # Unit and integration tests
├── docs/                                # Documentation, API references, theory
├── images/                              # Visual diagrams or illustrations
│
├── LICENSE                              # Open source license (e.g., MIT, Apache 2.0)
├── README.md                            # Project overview, usage, setup
├── CONTRIBUTING.md                      # Contribution guidelines for collaborators
├── requirements.txt                     # Python dependency specification
└── environment.yml                      # Conda environment setup

``` 


## 📜 Coding Standards
_____________________________________________________________
| **Category**  | **Standard**                              |
|---------------|-------------------------------------------|
| Language      | Python 3.10+                              |
| Style Guide   | PEP8 with `flake8`, `black`, `isort`      |
| Docstrings    | NumPy-style                               |
| Testing       | `pytest`, with ≥ 80% test coverage        |
| Type Hinting  | Required throughout the codebase          |
-------------------------------------------------------------


## 🔁 Branching Strategy

### ➤ Main Branches
- `main` – Stable, production-ready code
- `dev` – Integrated but in-development features (may fail CI)

### ➤ Feature Branch Naming

Use a consistent, scientific naming convention:
