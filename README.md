# 🧭 Quantum Vehicle Routing Problems – <br> Contribution & Structure Guide <br>


**Version:** 1.0  
**Last Updated:** July 19, 2025  
**Maintainers:** Dr. Raja Babu Jamatia & Dr. Paweł Gora 


---

## 🚀 Purpose

This repository aims to advance **Quantum and Hybrid Approaches** for solving a wide range of Vehicle Routing Problems (VRP), including:

- General VRP Models
- Capacitated VRP (CVRP)
- CVRP with Time Windows (CVRPTW)
  
It encourages development using Quantum-Inspired and Hybrid Quantum-Classical.

---




## 🧱 Repository Structure

```bash
Quantum-Vehicle-Routing-Problems/
│
├── Data/                                # Centralized input datasets
│   ├── CVRP/
│   ├── CVRPTW/
│   ├── VRP/
│   └── Global_Datasets/                  # similar Datasets for all
│       └── solomon/
│        
├── Variants/                             # Core logic grouped by VRP variants
│   ├── CVRP/
│   │   ├── solvers/
│   │   │   ├── __init__.py
│   │   │   ├── greedy_solver.py
│   │   │   ├── hybrid_solver.py
│   │   │   ├── qubo_dwave_solver.py
│   │   │   └── shared/                    # Shared logic local to CVRP solvers
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
│   │   │   └── shared/                     # Shared logic local to CVRPTW solvers
│   │   │       └── time_window_encoding.py
│   │   ├── problem.py
│   │   └── utils.py
│   │
│   └── VRP/
│       ├── solvers/
│       │   ├── baseline_solver.py
│       │   ├── qubo_classical_emulation.py
│       │   └── shared/                      # Placeholder if reusable components emerge
│       ├── problem.py
│       └── utils.py
│
├── Src/                                     # Shared core modules across all variants
│   ├── common/                              # Generic interfaces, models, helpers
│   │   ├── routing_problem.py
│   │   ├── routing_solution.py
│   │   └── dwave_helper.py
│   ├── encoding/
│   ├── preprocessing/
│   └── analysis/
│
├── Notebooks/                               # Jupyter notebooks for experimentation
├── Results/                                 # Output results, graphs, logs
├── Tests/                                   # Unit and integration tests
├── Docs/                                    # Documentation, API references, theory
├── Images/                                  # Visual diagrams or illustrations
│
├── LICENSE                                  # Open source license (e.g., MIT, Apache 2.0)
├── README.md                                # Project overview, usage, setup
├── CONTRIBUTING.md                          # Contribution guidelines for collaborators
├── Requirements.txt                         # Python dependency specification
└── Environment.yml                          # Conda environment setup

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

**Examples:**
- `feat/cvrptw-shared-qubo-refactor`
- `feat/unified-shared-qubo-architecture`

---

## ✅ New Contributor Checklist

1. **Fork** the repository
2. **Clone** your fork:
    ```bash
    git clone https://github.com/<your-username>/Quantum-Vehicle-Routing-Problems.git
    cd Quantum-Vehicle-Routing-Problems
    ```
3. **Create** a feature branch:
    ```bash
    git checkout -b feat/<scope>-<topic>
    ```
4. **Follow** the commit convention:
    ```
    <type>(<scope>): <summary>
    ```
    Example:
    ```
    refactor(CVRPTW): modularize shared encoding logic
    ```
5. **Add** documentation and unit tests
6. **Validate** all tests:
    ```bash
    pytest
    ```
7. **Push and Open** a PR to the `dev` branch

---

## 📁 File Sharing Guidelines

- Use `shared/` **within a variant** for intra-variant reusable logic
- Place cross-variant utilities under `src/`
- Avoid cyclic imports
- Keep utilities functional and minimal

---

## 🧪 Testing & Validation

Before pushing, run the full test suite:

```bash
pytest --cov=variants/ --cov=src/ --cov-report=term-missing
 ```
**⚠️ Note:** Pull Requests will only be merged when all CI checks pass.


## ⚠️ Elimination of Legacy Files

Legacy code (e.g., authored by Brennan) must be:

- Reviewed and documented
- Refactored into compliant structure or
- Removed if redundant/non-modular
🔒 Please contact maintainers before any deletion.

## 📌 Future Roadmap

Modular QUBO builders for improved scalability
Benchmarking standardization across solvers
Backend support:
- D-Wave Advantage
- Hybrid and Classical Simulators
Expansion into stochastic & dynamic VRP variants

## 🙌 Contributors and Roles

______________________________________________________________________________________________________________________________________________
|   **Name**                   |     **Role**                              |   **Contact**                                                     |
|------------------------------|-------------------------------------------|-------------------------------------------------------------------|
| Dr. Raja Babu Jamatia        |  Quantum Architect                        | <a href = "https://www.linkedin.com/in/pawelgora/">Click Me</a>   |
| Dr. Paweł Gora               |  Supervisor                               | <a href = "https://www.linkedin.com/in/pawelgora/">GO</a>   |
| Raphael Reeves               |                                           | <a href = "https://www.linkedin.com/in/User_Name/">Click Me</a>   | 
| Nafisa Shamim Rafa           |                                           | <a href = "https://www.linkedin.com/in/nafisa-shamim-rafa-6534131aa/">GO</a>   |
| Eshika Tripura Puja          |                                           | <a href = "https://www.linkedin.com/in/eshikatripura/">GO</a> |
| Mustafa Mert Ozyilmaz        |                                           | <a href = "https://www.linkedin.com/in/mustafa-mert6464/">GO</a> |
| Rithik Rai                   |                                           | <a href = "https://www.linkedin.com/in/iarithik/">GO</a> |
| Lohith Alladi                |                                           | <a href = "https://www.linkedin.com/in/User_Name/">Click Me</a>  |
| Risav Pokhrel                |                                           | <a href = "https://www.linkedin.com/in/risav-pokhrel/">GO</a> |
| Naman Bansal                 |                                           | <a href = "https://www.linkedin.com/in/User_Name/">Click Me</a> |
| Sadiya Ansari                |                                           | <a href = "https://www.linkedin.com/in/sadiyaansari2324/">GO</a> |
| Suprajit Dewanji             |                                           | <a href = "https://www.linkedin.com/in/User_Name/">Click Me</a> |
| sai sudarshan                |                                           | <a href = "https://www.linkedin.com/in/User_Name/">Click Me</a> |
| Abhishek Raj                 |                                           | <a href = "https://www.linkedin.com/in/User_Name/">Click Me</a> |
| Visalatchi R                 |                                           | <a href = "https://www.linkedin.com/in/User_Name/">Click Me</a> |
| Mohammad Abid Hafiz          |                                           | <a href = "https://www.linkedin.com/in/User_Name/">Click Me</a> |
| Hao Mack Yang                |                                           | <a href = "https://www.linkedin.com/in/User_Name/">Click Me</a> |
| Katarzyna Nałęcz-Charkiewicz |                                           |                                                                 |
-------------------------------------------------------------------------------------------------------------------------------------------------


## 📫 Contact & Community

Have questions, suggestions, or want to discuss quantum solvers?

- Open an Issue
- Start a conversation via GitHub Discussions
- Send an email to pawel.gora@qaif.org
<br>

**© 2025 Quantum-Vehicle-Routing-Problems**
