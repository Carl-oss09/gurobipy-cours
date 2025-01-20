import numpy as np
import gurobipy as gp
from gurobipy import GRB

def generate_knapsack(num_items):
    # Fix seed value
    rng = np.random.default_rng(seed=0)
    # Item values, weights
    values = rng.uniform(low=1, high=25, size=num_items)
    weights = rng.uniform(low=5, high=100, size=num_items)
    # Knapsack capacity
    capacity = 0.7 * weights.sum()

    return values, weights, capacity


def solve_knapsack_model(values, weights, capacity):
    num_items = len(values)
    
    # Convert numpy arrays to dictionaries for Gurobi
    items = range(num_items)
    value_dict = {i: values[i] for i in items}
    weight_dict = {i: weights[i] for i in items}

    with gp.Env() as env:
        with gp.Model(name="knapsack", env=env) as model:
            # Define decision variables
            x = model.addVars(items, vtype=GRB.BINARY, name="x")

            # Define the objective function: maximize the total value
            model.setObjective(x.prod(value_dict), GRB.MAXIMIZE)

            # Define the capacity constraint: total weight <= capacity
            model.addConstr(x.prod(weight_dict) <= capacity, name="capacity")

            # Optimize the model
            model.optimize()

            # Print the results
            if model.status == GRB.OPTIMAL:
                selected_items = [i for i in items if x[i].x > 0.5]
                total_value = sum(value_dict[i] for i in selected_items)
                total_weight = sum(weight_dict[i] for i in selected_items)
                
                print(f"Selected items: {selected_items}")
                print(f"Total value: {total_value}")
                print(f"Total weight: {total_weight}")
            else:
                print("No optimal solution found.")


# Generate data and solve the knapsack problem
data = generate_knapsack(10000)
solve_knapsack_model(*data)
