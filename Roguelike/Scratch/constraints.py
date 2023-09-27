from ortools.sat.python import cp_model

# Create a model
model = cp_model.CpModel()

# Define variables
wealth_A = model.NewIntVar(0, 10, "wealth_A")
wealth_B = model.NewIntVar(0, 10, "wealth_B")
wealth_C = model.NewIntVar(0, 10, "wealth_C")

# Define constraints
model.Add(wealth_A + wealth_B > wealth_C)  # A + B should have more wealth than C
model.Add(wealth_B >= 2 * wealth_A)        # B should have at least twice the wealth of A

# Create a solver and solve
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Extract and print the solution
if status == cp_model.OPTIMAL:
    print("Wealth of Region A:", solver.Value(wealth_A))
    print("Wealth of Region B:", solver.Value(wealth_B))
    print("Wealth of Region C:", solver.Value(wealth_C))
else:
    print("No solution found.")
