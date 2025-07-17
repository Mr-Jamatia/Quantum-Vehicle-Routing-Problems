# 🧭 Quantum Vehicle Routing Problems – <br> Contribution & Structure Guide <br>


**Version:** 1.0  
**Last Updated:** July 17, 2025  
**Maintainers:** Dr. Raja Babu Jamatia



# 🤝 Contributing to Quantum Vehicle Routing Problems (QVRP)

Welcome! 🎉

We appreciate your interest in contributing to the **Quantum-Vehicle-Routing-Problems (QVRP)** project. This repository is built with scientific rigor and collaborative spirit. Whether you're fixing a typo, improving code efficiency, or adding entirely new features—your contribution is valuable.

---

## 📋 Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Ground Rules](#ground-rules)
3. [Getting Started](#getting-started)
4. [Branching Strategy](#branching-strategy)
5. [Commit Guidelines](#commit-guidelines)
6. [Coding Standards](#coding-standards)
7. [Testing & CI](#testing--ci)
8. [Legacy Files Policy](#legacy-files-policy)
9. [Pull Request Process](#pull-request-process)
10. [Community & Support](#community--support)

---



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
- IBM Q
- Hybrid Simulators
Expansion into stochastic & dynamic VRP variants

## 🙌 Contributors and Roles

Name	Role
Dr. Raja Babu Jamatia	Quantum Architect, Core Contributor
Pawet Gora	Optimization Lead
Brennan	Legacy Structure Architect

## 📫 Contact & Community

Have questions, suggestions, or want to discuss quantum solvers?

Open an Issue
Start a conversation via GitHub Discussions
© 2025 Quantum-Vehicle-Routing-Problems
