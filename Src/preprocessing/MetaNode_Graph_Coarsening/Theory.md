The goal is not to solve the CVRPTW, but to abstract it into a smaller, high-fidelity equivalent.This is achieved by clustering original customers into a smaller set of meta-nodes . 
The core of the decision-making process is the CompatibilityScore, a weighted sum of three normalized penalty functions. A lower score indicates a more desirable merge.
Score(A, B) = wc · Pc(A, B) + wd · Pd(A, B) + wt· Pt(A, B) (1)
where wc, wd, wt are tunable weights (e.g., 0.4, 0.2, 0.4).
1. Cost Penalty (Pc): Penalizes large geographical separation to encourage dense, local clusters.
It is the normalized travel time tAB.
2. Demand Penalty (Pd): Penalizes high consumption of vehicle capacity Q. If dA + dB > Q,
the penalty is infinite, making the merge impossible.
3. Time Penalty (Pt): Penalizes temporal inflexibility. It is calculated based on the ”time slack”
available between two nodes, heavily penalizing pairs with little to no buffer time.

When a pair of nodes (A, B) is merged into a new meta-node M, its properties are aggregated with
mathematical rigor:
• Aggregated Demand (dM): dM = dA + dB
• Aggregated Service Time (sM): Includes internal travel time. For an A → B sequence:
sM = sA + tAB + sB
• Aggregated Coordinates (xM, yM): A demand-weighted center of mass.
• Tightened Time Window ([eM, lM]): This is the most critical calculation, ensuring the
feasibility of the stored internal sequence. For an A → B sequence:
eM = eA (2)
lM = min(lA, lB − sA − tAB − sB) (3)
This formula correctly bakes in all intermediate time costs. A merge is only feasible if eM ≤ lM.
