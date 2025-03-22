import requests
from bs4 import BeautifulSoup
import csv
import urllib.parse
import time

def fetch_country_names(url):
    try:
        # Définir les en-têtes HTTP pour imiter un navigateur 
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                          'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                          'Chrome/58.0.3029.110 Safari/537.3'
        }
        
        # Envoyer une requête GET à l'URL avec les en-têtes
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Vérifie si la requête a réussi
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête HTTP: {e}")
        return []

    # Parser le contenu HTML avec BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Trouver le tableau contenant les pays en recherchant le <table> avec la classe "related_links"
    table = soup.find('table', class_='related_links')
    if not table:
        print("Tableau avec la classe 'related_links' non trouvé dans la page.")
        return []

    country_names = []

    # Parcourir tous les éléments <a> dans le tableau
    for a_tag in table.find_all('a', href=True):
        country_name = a_tag.get_text(strip=True)
        if country_name:
            country_names.append(country_name)

    return country_names

def construct_urls(base_url, country_names):
    country_data = []
    for name in country_names:
        # Encoder le nom du pays pour l'URL (remplacer les espaces par +, etc.)
        encoded_name = urllib.parse.quote_plus(name)
        # Construire l'URL avec le paramètre displayCurrency=EUR
        full_url = f"{base_url}?country={encoded_name}&displayCurrency=EUR"
        country_data.append({
            'Nom': name,
            'URL': full_url
        })
    return country_data

def parse_country_page(country_name, url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                          'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                          'Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête HTTP pour {country_name}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Trouver toutes les tables avec la classe "data_wide_table new_bar_table"
    tables = soup.find_all('table', class_='data_wide_table new_bar_table')
    if not tables:
        print(f"Aucune table 'data_wide_table new_bar_table' trouvée pour {country_name}.")
        return []

    country_info = []

    for table in tables:
        current_category = None
        for row in table.find_all('tr'):
            # Vérifier si la ligne contient un en-tête de catégorie
            th = row.find('th', class_='highlighted_th')
            if th:
                # Extraire le nom de la catégorie
                category_div = th.find('div', class_='category_title')
                if category_div:
                    current_category = category_div.get_text(strip=True)
                continue  # Passer à la prochaine ligne

            # Extraire les données de la ligne
            cells = row.find_all('td')
            if len(cells) >= 2:
                item = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True).replace('\xa0', ' ')
                
                # Extraire la plage si disponible
                if len(cells) >= 3:
                    range_text = cells[2].get_text(strip=True).replace('\xa0', ' ')
                else:
                    range_text = ''

                # Ajouter les informations extraites
                country_info.append({
                    'Pays': country_name,
                    'Catégorie': current_category,
                    'Item': item,
                    'Valeur': value,
                    'Plage': range_text
                })

    return country_info

def save_to_csv(data, filename):
    if not data:
        print("Aucune donnée à sauvegarder.")
        return

    # Déterminer les en-têtes à partir des clés du premier dictionnaire
    headers = data[0].keys()

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
        print(f"Données sauvegardées dans {filename}")
    except IOError as e:
        print(f"Erreur lors de l'écriture du fichier CSV: {e}")

def main():
    base_url = "https://www.numbeo.com/property-investment/country_result.jsp"
    target_url = "https://www.numbeo.com/property-investment/"

    print(f"Récupération des noms des pays depuis {target_url}...")
    country_names = fetch_country_names(target_url)

    if not country_names:
        print("Aucune donnée de pays récupérée. Fin du script.")
        return

    print(f"{len(country_names)} pays trouvés.")
    # Afficher les premiers résultats
    for country in country_names[:10]:
        print(f"{country}")

    # Construire les URLs complètes avec displayCurrency=EUR
    country_data = construct_urls(base_url, country_names)

    all_country_info = []

    for idx, country in enumerate(country_data, start=1):
        name = country['Nom']
        url = country['URL']
        print(f"\n[{idx}/{len(country_data)}] Récupération des données pour {name}...")
        country_info = parse_country_page(name, url)
        if country_info:
            all_country_info.extend(country_info)
            print(f"  {len(country_info)} entrées ajoutées pour {name}.")
        else:
            print(f"  Aucune donnée ajoutée pour {name}.")
        
        # Pause pour éviter de surcharger le serveur
        time.sleep(1)  # Attendre 1 seconde entre les requêtes

    # Sauvegarder toutes les données dans un fichier CSV
    save_to_csv(all_country_info, 'donnees_pays_numbeo.csv')

if __name__ == "__main__":
    main()
