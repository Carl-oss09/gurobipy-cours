import json
import pandas as pd
import numpy as np
import gurobipy as gp
from gurobipy import GRB

# Charger les données du fichier JSON
with open("data/portfolio-example.json", "r") as f:
    data = json.load(f)

# Extraire les informations nécessaires
n = data["num_assets"]
sigma = np.array(data["covariance"])  # Covariance des actifs
mu = np.array(data["expected_return"])  # Rendement attendu des actifs
mu_0 = data["target_return"]  # Rendement cible du portefeuille
k = data["portfolio_max_size"]  # Taille maximale du portefeuille

# Créer le modèle d'optimisation
with gp.Model("portfolio") as model:
    # Variables de décision : x_i = investissement dans l'actif i
    x = model.addVars(n, vtype=GRB.CONTINUOUS, name="x")
    
    # Variables binaires y_i pour savoir si l'actif i est inclus dans le portefeuille
    y = model.addVars(n, vtype=GRB.BINARY, name="y")
    
    # Fonction objectif : minimiser le risque du portefeuille (variance)
    portfolio_risk = gp.quicksum(sigma[i][j] * x[i] * x[j] for i in range(n) for j in range(n))
    model.setObjective(portfolio_risk, GRB.MINIMIZE)
    
    # Contrainte 1 : la somme des poids d'investissement doit être égale à 1
    model.addConstr(gp.quicksum(x[i] for i in range(n)) == 1, "total_investment")
    
    # Contrainte 2 : le rendement attendu du portefeuille doit être supérieur ou égal au rendement cible
    model.addConstr(gp.quicksum(mu[i] * x[i] for i in range(n)) >= mu_0, "target_return")
    
    # Contrainte 3 : la taille maximale du portefeuille (nombre d'actifs sélectionnés)
    model.addConstr(gp.quicksum(y[i] for i in range(n)) <= k, "max_portfolio_size")
    
    # Contrainte 4 : un actif ne peut être sélectionné que si une certaine proportion est investie
    for i in range(n):
        model.addConstr(x[i] <= y[i], f"invest_if_selected_{i}")
    
    # Optimiser le modèle
    model.optimize()

    # Extraire et afficher les résultats
    if model.status == GRB.OPTIMAL:
        portfolio = [x[i].X for i in range(n)]
        risk = model.ObjVal
        expected_return = gp.quicksum(mu[i] * x[i].X for i in range(n))

        # Créer le DataFrame pour afficher les résultats du portefeuille
        df = pd.DataFrame(
            data=portfolio + [risk, expected_return],
            index=[f"asset_{i}" for i in range(n)] + ["risk", "return"],
            columns=["Portfolio"]
        )
        print(df)

        # Afficher les actifs sélectionnés
        selected_assets = [i for i in range(n) if y[i].X > 0.5]
        print(f"Assets selected for the portfolio: {selected_assets}")
    else:
        print("Aucune solution optimale trouvée.")
