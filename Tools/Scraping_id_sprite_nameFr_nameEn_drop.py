import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def capitalize_first_letter(word):
    if not word:
        return word
    return word[0].upper() + word[1:] if word else word

def clean_french_name(name_fr):
    name_fr = re.sub(r'<[^>]+>', '', name_fr)
    name_fr = re.sub(r'<br>.*', '', name_fr)
    name_fr = re.sub(r'\(.*\)', '', name_fr)
    name_fr = re.sub(r'Forme.*', '', name_fr)
    name_fr = re.sub(r'forme.*', '', name_fr)
    name_fr = name_fr.strip()
    return name_fr

def extract_main_french_name(col):
    small_elements = col.find_all('small')
    for small in small_elements:
        small.decompose()
    name_fr = col.get_text(strip=True)
    name_fr = clean_french_name(name_fr)
    return name_fr

def scrape_drops():
    url_drops = 'https://wiki.cobblemon.com/index.php/Pokémon/Drops'
    response_drops = requests.get(url_drops)
    soup_drops = BeautifulSoup(response_drops.content, 'html.parser')

    pokemon_drops = {}

    tables = soup_drops.find_all('table')
    for table in tables:
        rows = table.find_all('tr')[1:]
        for row in rows:
            th_elements = row.find_all('th')
            td_elements = row.find_all('td')

            if len(th_elements) >= 1 and len(td_elements) >= 2:
                drop_name = th_elements[0].get_text(strip=True)
                number = td_elements[0].get_text(strip=True)
                drops_quantity = td_elements[2].get_text(strip=True)

                number_clean = number[1:] if number.startswith('#') else number

                if number_clean in pokemon_drops:
                    pokemon_drops[number_clean] += f", {drop_name} ({drops_quantity})"
                else:
                    pokemon_drops[number_clean] = f"{drop_name} ({drops_quantity})"

    return pokemon_drops

def translate_drops(drops_str, pokemon_items_df, minecraft_items_df):
    item_dict = {}

    for _, row in pokemon_items_df.iterrows():
        item_dict[row['English'].lower()] = row['Français']

    for _, row in minecraft_items_df.iterrows():
        item_dict[row['English'].lower()] = row['Français']

    def translate_item(match):
        english_item = match.group(1).strip().lower()
        return item_dict.get(english_item, match.group(0))

    pattern = re.compile(r'(\b[A-Za-z\s]+\b)')
    translated_drops = pattern.sub(translate_item, drops_str)

    return translated_drops

# URLs for scraping
url_fr = 'https://www.pokepedia.fr/Liste_des_Pokémon_dans_l%27ordre_du_Pokédex_National'
url_en = 'https://cobblemon.tools/pokedex/'

# Fetching and parsing HTML content
response_fr = requests.get(url_fr)
soup_fr = BeautifulSoup(response_fr.content, 'html.parser')

response_en = requests.get(url_en)
soup_en = BeautifulSoup(response_en.content, 'html.parser')

# Scraping and processing data
pokemon_fr = {}
tables_fr = soup_fr.find_all('table')
if len(tables_fr) >= 3:
    table = tables_fr[2]
    rows = table.find_all('tr')[1:]
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 3:
            number_fr = cols[0].get_text(strip=True)
            name_fr = extract_main_french_name(cols[2])
            pokemon_fr[number_fr] = name_fr
else:
    print("La troisième table n'a pas été trouvée.")

text_en = soup_en.get_text()
sections_en = text_en.split('\n\n')[1:]

pokemon_base_en = {}

for section in sections_en:
    lines = section.split('\n')
    if len(lines) > 1:
        if lines and lines[1].startswith('#'):
            number = lines[1].strip()
            number_clean = number[1:] if number.startswith('#') else number
            if number_clean not in pokemon_base_en:
                if len(lines) > 2:
                    name_en = lines[2].strip()
                    name_en = capitalize_first_letter(name_en)
                    img_url = f"https://cobblemon.tools/pokedex/pokemon/{name_en.lower()}/sprite.png"
                    pokemon_base_en[number_clean] = {
                        'Nom en anglais': name_en,
                        'URL de l\'image': img_url
                    }

# Scrape drops
pokemon_drops = scrape_drops()

# Load CSV files for translation
pokemon_items_df = pd.read_csv('dict_en-fr_pokemon_items.csv')
minecraft_items_df = pd.read_csv('dict_en-fr_minecraft_items.csv')

# Creating a DataFrame for storing the information
data = []
for number_clean in pokemon_base_en:
    name_en = pokemon_base_en[number_clean]['Nom en anglais']
    img_url = pokemon_base_en[number_clean]['URL de l\'image']
    name_fr = pokemon_fr.get(number_clean, '')
    drops = pokemon_drops.get(number_clean, '')
    translated_drops = translate_drops(drops, pokemon_items_df, minecraft_items_df)
    data.append({
        'Numéro': f'#{number_clean}',
        'Nom en français': name_fr,
        'Nom en anglais': name_en,
        'URL de l\'image': img_url,
        'Drop': translated_drops
    })

df = pd.DataFrame(data)

# Save the data to a CSV file
df.to_csv('pokemon_data.csv', index=False)

# Create a Markdown table
markdown_table = "| Numéro de Pokémon | Sprite du Pokémon | Nom en français | Nom en anglais | Drop | Zone de spawn | Move spécial |\n"
markdown_table += "|-------------------|--------------------|------------------|-----------------|------|---------------|--------------|\n"

for index, row in df.iterrows():
    number = row['Numéro']
    name_fr = row['Nom en français']
    name_en = row['Nom en anglais']
    sprite_url = row['URL de l\'image']
    drops = row['Drop']
    sprite_markdown = f"![{name_en}]({sprite_url})"
    markdown_table += f"| {number} | {sprite_markdown} | {name_fr} | {name_en} | {drops} | | |\n"

# Save the Markdown table to a file
with open('pokemon_table.md', 'w', encoding='utf-8') as f:
    f.write(markdown_table)

print("Tableau Markdown créé avec succès dans pokemon_table.md")
