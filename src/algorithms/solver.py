from typing import Dict, List, Tuple
from ortools.linear_solver import pywraplp


def solve(matrix: List[List[int]]) -> Tuple[Dict[int, int], float]:
    O = 999

    # Number of orders
    num_orders = len(matrix[0])

    # Update matrix costs with dummy rider
    matrix.append([O for _ in range(num_orders)])

    # Create number of riders and orders
    num_riders = len(matrix)

    # Create solver
    solver = pywraplp.Solver.CreateSolver("SCIP")

    # Variables
    # x[i, j] is an array of 0-1 variables, which will be 1
    # if rider i is assigned to order j.
    x = {}
    for i in range(num_riders):
        for j in range(num_orders):
            if matrix[i][j] != "NA":
                x[i, j] = solver.IntVar(0, 1, "")

    # Constraints
    # Each rider except the last (dummy rider) is assigned to at most 1 order.
    for i in range(num_riders - 1):
        solver.Add(
            solver.Sum([x[i, j] for j in range(num_orders) if matrix[i][j] != "NA"])
            <= 1
        )

        # Each order is assigned to exactly one rider.
    for j in range(num_orders):
        solver.Add(
            solver.Sum([x[i, j] for i in range(num_riders) if matrix[i][j] != "NA"])
            == 1
        )

    # Objective
    objective_terms = []
    for i in range(num_riders):
        for j in range(num_orders):
            if matrix[i][j] != "NA":
                objective_terms.append(matrix[i][j] * x[i, j])
    solver.Minimize(solver.Sum(objective_terms))

    # Solve
    solver.Solve()

    # Return solution as dictionary {rider : order}
    solution = {}
    for i in range(num_riders - 1):
        for j in range(num_orders):
            if matrix[i][j] != "NA":
                if x[i, j].solution_value() == 1.0:
                    solution[i] = j

    return (solution, solver.Objective().Value())
