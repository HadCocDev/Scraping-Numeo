import pandas as pd
import re

def nettoyer_valeur(x):
    if pd.isna(x):
        return None
    # Supprimer le symbole '€' et tout caractère superflu
    x = x.replace('€', '').strip().replace(',', '.')
    # Extraire le premier nombre (cela fonctionnera même si la chaîne contient une plage ou du texte supplémentaire)
    match = re.search(r"[-+]?[0-9]*\.?[0-9]+", x)
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None
    return None

def nettoyer_plage(x):
    if pd.isna(x) or x.strip() == '':
        return None
    # Remplacer le symbole '€' et uniformiser
    x = x.replace('€', '').strip().replace(',', '.')
    # Rechercher un motif de type "nombre - nombre"
    match = re.search(r"([-+]?[0-9]*\.?[0-9]+)\s*-\s*([-+]?[0-9]*\.?[0-9]+)", x)
    if match:
        try:
            mini = float(match.group(1))
            maxi = float(match.group(2))
            return (mini, maxi)
        except ValueError:
            return None
    return None

def nettoyage_donnees(df):
    # Supprimer les lignes totalement vides
    df = df.dropna(how='all')
    
    # Uniformiser les chaînes de caractères pour les colonnes textuelles
    if 'Pays' in df.columns:
        df['Pays'] = df['Pays'].str.strip().str.lower()
    if 'Catégorie' in df.columns:
        df['Catégorie'] = df['Catégorie'].str.strip().str.lower()
    if 'Item' in df.columns:
        df['Item'] = df['Item'].str.strip().str.lower()
    
    # Nettoyer la colonne 'Valeur'
    if 'Valeur' in df.columns:
        df['Valeur_nettoyee'] = df['Valeur'].apply(nettoyer_valeur)
    
    # Extraire la plage sous forme de deux colonnes si besoin
    if 'Plage' in df.columns:
        df['Plage_nettoyee'] = df['Plage'].apply(nettoyer_plage)
        # On peut également séparer en deux colonnes distinctes pour le minimum et le maximum
        df['Plage_min'] = df['Plage_nettoyee'].apply(lambda x: x[0] if isinstance(x, tuple) else None)
        df['Plage_max'] = df['Plage_nettoyee'].apply(lambda x: x[1] if isinstance(x, tuple) else None)
    
    # Conserver uniquement les lignes ayant une valeur numérique nettoyée
    df = df.dropna(subset=['Valeur_nettoyee'])
    
    return df

def main():
    input_file = 'donnees_pays_numbeo.csv'
    output_file = 'donnees_pays_nettoye.csv'
    
    try:
        df = pd.read_csv(input_file, encoding='utf-8')
    except FileNotFoundError:
        print(f"Le fichier {input_file} n'a pas été trouvé.")
        return
    
    print("Nettoyage des données...")
    df_nettoye = nettoyage_donnees(df)
    
    df_nettoye.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Données nettoyées sauvegardées dans {output_file}.")

if __name__ == '__main__':
    main()
