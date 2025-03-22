import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import numpy as np

def main():
    # Charger les données nettoyées
    input_file = 'donnees_pays_nettoye.csv'
    try:
        df = pd.read_csv(input_file, encoding='utf-8')
    except FileNotFoundError:
        print(f"Le fichier {input_file} n'a pas été trouvé.")
        return

    # Utiliser la colonne 'Item' pour prédire 'Valeur_nettoyee'
    X = df[['Item']]
    y = df['Valeur_nettoyee']

    # Séparer en ensembles d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Créer un pipeline avec OneHotEncoder et LinearRegression
    pipeline = make_pipeline(
        OneHotEncoder(sparse_output=False, handle_unknown='ignore'),
        LinearRegression()
    )

    # Entraîner le modèle
    pipeline.fit(X_train, y_train)

    # Prédire sur l'ensemble de test
    y_pred = pipeline.predict(X_test)

    # Calculer la performance (MSE et SSE)
    mse = mean_squared_error(y_test, y_pred)
    sse = np.sum((y_test - y_pred) ** 2)

    print("Performance (régression) :")
    print("  Erreur quadratique moyenne (MSE) :", mse)
    print("  Somme des carrés des erreurs (SSE)   :", sse)

    # Exemple d'inférence sur une nouvelle donnée en passant un DataFrame pour éviter le warning
    nouveau_df = pd.DataFrame({'Item': ['prix']})
    prediction = pipeline.predict(nouveau_df)
    print(f"\nPour l'item 'prix', la prédiction de 'Valeur_nettoyee' est : {prediction[0]}")

if __name__ == '__main__':
    main()
