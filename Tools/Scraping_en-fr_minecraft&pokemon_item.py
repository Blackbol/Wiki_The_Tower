import requests
from bs4 import BeautifulSoup
import pandas as pd

# URLs des sites web à scraper
minecraft_object_url = "https://fr-minecraft.net/4-outils-et-objets-dans-minecraft.php"
minecraft_bloc_url = "https://fr-minecraft.net/3-differents-blocs-jeu.php"

minecraft_items = {'English': "Turtle Scute", 'Français': "Carapace de tortue"}, \
                  {'English': "Armadillo Scute", 'Français': "Écaille de tatou"}, \
                  {'English': "Dragon's Breath", 'Français': "Souffle de dragon"}, \
                  {'English': "Rabbit's Foot", 'Français': "Patte de lapin"}


pokemon_url = "https://www.pokemontrash.com/pokedex/liste-objets.php"

pokemon_items = {'English': "Wepear Berry", 'Français': "Baie Wepear"}, \
                {'English': "Bluk Berry", 'Français': "Baie Bluk"}, \
                {'English': "Razz Berry", 'Français': "Baie Razz"}, \
                {'English': "Nanab Berry", 'Français': "Baie Nanab"}, \
                {'English': "Fairy Feather", 'Français': "Plume Enchantée"}, \
                {'English': "King's Rock", 'Français': "Roche Royale"}, \
                {'English': "Auspicious Armor", 'Français': "Armure de la Fortune"}, \
                {'English': "Malicious Armor", 'Français': "Armure de la Rancune"}, \
                {'English': "Misty Seed", 'Français': "Graine Brume"}, \
                {'English': "Ability Shield", 'Français': "Garde-Talent"}, \
                {'English': "Pierre Glace", 'Français': "Ice Stone"}, \
                {'English': "Pierre Foudre", 'Français': "Thunder Stone"}, \
                {'English': "Bright Powder", 'Français': "Poudre Claire"}, \
                {'English': "Never-Melt Ice", 'Français': "Glace Éternelle"}, \
                {'English': "Medicinal Leek", 'Français': "Soignon"}, \
                {'English': "Relic Coin", 'Français': "Pièce Relique"}, \
                {'English': "	Peat Block", 'Français': "Bloc de Tourbe"}, \
                {'English': "Pinap Berry", 'Français': "Baie Pinap"}
                

def scrape_minecraft_items(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    items = []

    for a_tag in soup.find_all('a', class_='content_popup_link'):
        french_name = a_tag.text.strip()
        span_tag = a_tag.find_next('span', class_='english')
        if span_tag:
            english_name = span_tag.text.strip()
            items.append({'English': english_name, 'Français': french_name})

    for item in minecraft_items:
        items.append(item)
    
    return pd.DataFrame(items)

def scrape_pokemon_items(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    items = []

    # Adapter les sélecteurs CSS pour correspondre à la structure HTML du site Pokémon
    rows = soup.select('#content > div.zen > article > table > tbody > tr')
    for row in rows:
        french_name_tag = row.select_one('td:nth-child(2) > a')
        english_name_tag = row.select_one('td:nth-child(3) > em')

        if french_name_tag and english_name_tag:
            french_name = french_name_tag.text.strip()
            if 'band.' in french_name:
                french_name = french_name.replace('band.', 'Bandeau ')
            if 'Lunet.' in french_name:
                french_name = french_name.replace('Lunet.', 'Lunettes ')
            if 'Arg.' in french_name:
                french_name = french_name.replace('Arg.', 'Argentée')
            if 'Purif.' in french_name:
                french_name = french_name.replace('Purif.', 'Purifiante')
            if 'Charbon' in french_name:
                french_name = french_name.replace('Charbon', 'Bâton de charbon')
            if 'Cuillertordu' in french_name:
                french_name = french_name.replace('Cuillertordu', 'Cuillère Tordue')
            if 'Pierrefoudre' in french_name:
                french_name = french_name.replace('Pierrefoudre', 'Pierre Foudre')
            if 'Pierreplante' in french_name:
                french_name = french_name.replace('Pierreplante', 'Pierre Plante')
            if 'Rune Purif.' in french_name:
                french_name = french_name.replace('Rune Purif.', 'Rune Purifiante')
            if 'Ballelumière' in french_name:
                french_name = french_name.replace('Ballelumière', 'Balle Lumière')
            if 'Grosseracine' in french_name:
                french_name = french_name.replace('Grosseracine', 'Grosse Racine')
            english_name = english_name_tag.text.strip()
            if 'Charcoal' in english_name:
                english_name = english_name.replace('Charcoal', 'Charcoal Stick')
            items.append({'English': english_name, 'Français': french_name})

    # add item
    for item in pokemon_items:
        items.append(item)

    return pd.DataFrame(items)

# Extraire les objets Minecraft et Pokémon
minecraft_objet_df = scrape_minecraft_items(minecraft_object_url)
minecraft_bloc_df = scrape_minecraft_items(minecraft_bloc_url)
pokemon_df = scrape_pokemon_items(pokemon_url)

# Créer un DataFrame avec les objets et l'exporter en CSV
items_df = pd.concat([minecraft_objet_df, minecraft_bloc_df], ignore_index=True)
items_df.to_csv('dict_en-fr_minecraft_items.csv', index=False)
print("Fichier dict_en-fr_minecraft_items CSV généré avec succès.")

# Créer un DataFrame avec les objets et l'exporter en CSV
items_df = pd.DataFrame(pokemon_df)
items_df.to_csv('dict_en-fr_pokemon_items.csv', index=False)
print("Fichier dict_en-fr_pokemon_items CSV généré avec succès.")
