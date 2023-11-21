import requests
from bs4 import BeautifulSoup
import json
import time
import random
import pandas as pd

def get_information_from_verb(verb):
    verb = verb.strip().lower()

    # Construct the URL
    url = f"https://en.wiktionary.org/wiki/{verb}#Latin"

    # Define a user-agent string
    headers = {
        'User-Agent': 'Scraping Latin Verb Conjs for personal practice (leander.parton@hotmail.com)'
    }
    
    # Get the page content
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raises HTTPError if the HTTP request returned an unsuccessful status code
    
    # Parse the HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the declension table
    tables = soup.find_all('table', class_='inflection-table')
    latin_table = None
    for table in tables:
        if 'inflection-table' in table.get('class', []):
            # Check if the inflection table is for Latin
            # Get first th
            th = table.find('th')
            # Get th's i
            i = th.find('i')
            if i is None:
                continue
            lang = i.get('lang')
            if lang == "la":
                latin_table = table
                break
            else:
                continue

    if not latin_table:
        print("No Latin inflection table found on the page.")
        return "Conjugation table not found for the given verb."
    

    conjs = []
    translations = []
    wordclass = None
    for row in latin_table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) > 1:
            for i in range(len(list(cells))):
                textcont = str(list(cells)[i])
                # If textcont contains "form-of lang-la", print textcont
                if "form-of lang-la" in textcont:
                    # Print the text between "form-of lang-la" and "-form-of"
                    text = textcont[textcont.find("form-of lang-la")+16:textcont.find("-form-of")]
                    cnt = cells[i].get_text(strip=True)
                    if "," in cnt:
                        cnt = cnt[:cnt.find(",")]
                    conjs.append([text, cnt])
        longcells = row.find_all('th')
        if len(longcells) > 1:
            for i in range(len(list(longcells))):
                if longcells[i].get('colspan') == '6':
                    cont = longcells[i].get_text(strip=True)
                    if "present active indicative ofsum" in cont:
                        c = "1|s|perf|pass|ind"
                        cnt = cont[:cont.find("+ present active indicative ofsum")] + " sum"
                        conjs.append([c, cnt])
                    if "imperfect active indicative ofsum" in cont:
                        c = "1|s|plup|pass|ind"
                        cnt = cont[:cont.find("+ imperfect active indicative ofsum")] + " eram"
                        conjs.append([c, cnt])
                    if "future active indicative ofsum" in cont:
                        c = "1|s|futp|pass|ind"
                        cnt = cont[:cont.find("+ future active indicative ofsum")] + " ero"
                        conjs.append([c, cnt])
                    if "present active subjunctive ofsum" in cont:
                        c = "1|s|perf|pass|sub"
                        cnt = cont[:cont.find("+ present active subjunctive ofsum")] + " sim"
                        conjs.append([c, cnt])
                    if "imperfect active subjunctive ofsum" in cont:
                        c = "1|s|plup|pass|sub"
                        cnt = cont[:cont.find("+ imperfect active subjunctive ofsum")] + " essem"
                        conjs.append([c, cnt])

    if response.ok:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the Latin section by an 'id' that matches 'Latin'
        latin_section = soup.find('span', {'id': 'Latin'})
        
        # If the Latin section is present, proceed to find the translations table
        if latin_section:
            # Navigate up to the parent 'h2' and then to the following 'ol' element
            ol_tag = latin_section.find_parent('h2').find_next_sibling('ol')
            
            if ol_tag.find_previous_sibling('h4'):
                if ol_tag.find_previous_sibling('h4').find_previous_sibling("h2").get_text() == "Latin[edit]":
                    wordclass = ol_tag.find_previous_sibling('h4').get_text()
                else: 
                    wordclass = ol_tag.find_previous_sibling('h3').get_text()
            else: 
                wordclass = ol_tag.find_previous_sibling('h3').get_text()
            
            if ol_tag:
                # Find all 'li' elements, which should contain the translations
                for li in ol_tag.find_all('li'):
                    children = li.contents
                    non_string_children = [child for child in children if not isinstance(child, str)]
                    if non_string_children:
                        if non_string_children[0].name in ["div", "b"]:
                            continue
                    dl = li.find('dl')
                    if dl:
                        translation = li.get_text()[:li.get_text().find(dl.get_text())]
                    else:
                        translation = li.get_text()
                    # Translation equals translation up to first \n, if \n exists
                    if "\n" in translation:
                        translation = translation[:translation.find("\n")]
                    translations.append(translation)
            else:
                print("No translations found in the ordered list.")
        else:
            print("No Latin section found on the page.")
    else:
        print(f"Error fetching the page: {response.status_code}")

    num = 0
    if response.ok:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the Latin section by an 'id' that matches 'Latin'
        latin_section = soup.find('span', {'id': 'Latin'})
        
        # If the Latin section is present, proceed to find the translations table
        if latin_section:
            # Navigate up to the parent 'h2' and then to the following 'ol' element
            ol_tag = latin_section.find_parent('h2')
            currtag = ol_tag.find_next_sibling("h4")
            stop = False
            while not stop:
                if currtag.get_text() == "Conjugation[edit]":
                    stop = True
                else:
                    if currtag.find_next_sibling("h5"):
                        if currtag.find_next_sibling("h5").find_previous_sibling("h2").get_text() == "Latin[edit]":
                            currtag = currtag.find_next_sibling("h5")
                            continue
                        else:
                            pass
                    if currtag.find_next_sibling("h4"):
                        if currtag.find_next_sibling("h4").find_previous_sibling("h2").get_text() == "Latin[edit]":
                            currtag = currtag.find_next_sibling("h4")
                        else:
                            print("No Latin section found for verb " + verb)
                            stop = True
                    else:
                        print("No Latin section found for verb " + verb)
                        stop = True
            conjtag = currtag.find_next_sibling("table").find("th").get_text()
            if "first" in conjtag:
                num = "1"
            elif "second" in conjtag:
                num = "2"
            elif "third" in conjtag:
                if "iō-variant" in conjtag:
                    num = "3io"
                else:
                    num = "3"
            elif "fourth" in conjtag:
                num = "4"
            elif "irregular" in conjtag:
                num = "irreg"
            else:
                print("No Latin section found for verb " + verb)
        else:
            print("No Latin section found for verb " + verb)
    else:
        print(f"Error fetching the page: {response.status_code}")

    return conjs, translations, wordclass, num


def save_info(verb, all_data):
    # Check if the verb is already processed
    if verb in [v['latin'] for v in all_data]:
        print(f"The verb '{verb}' is already processed.")
        return 0

    # Get the information from the verb
    conjugations, translations, wordclass, conjugationType = get_information_from_verb(verb)

    # Format the conjugations into a dictionary
    conjugations_dict = {c[0]: c[1] for c in conjugations}

    # Append the new verb information to the list
    new_verb_info = {
        "latin": verb,
        "translation": translations if translations else "No translation found",
        "conjugationType": conjugationType,
        "conjugations": conjugations_dict
    }
    all_data.append(new_verb_info)
    return 1

def initialize_data():
    # Get all verbs from lat.json and return pandas dataframe
    with open('lat.json', 'r') as file:
        data = json.load(file)
    pdf = pd.DataFrame(data['verbs'])
    return pdf

def demacronize(word):
    return word.replace("ā", "a").replace("ē", "e").replace("ī", "i").replace("ō", "o").replace("ū", "u").replace("ȳ", "y")


def get_conjug(verb, conj=None, pdf=None, demacronizing=True):
    if pdf is None:
        pdf = initialize_data()
    c = pdf[pdf['latin'] == verb]['conjugations']
    if conj is None:
        # Extract keys from all dictionaries in the Series
        a = [key for item in c if isinstance(item, dict) for key in item.keys()]
        return a
    else:
        # Find the first non-empty dictionary in the Series and access the desired conjugation
        for item in c:
            if isinstance(item, dict) and conj in item:
                return demacronize(item[conj]) if demacronizing else item[conj]
        # If no matching conjugation is found
        return None



def get_latin_verb_conjugation(verb, person="1", number="s", tense="pres", mood="ind", voice="act", infinites="none", case="none", conjugation=None):
    if conjugation is not None:
        conj = conjugation
    elif infinites.lower() not in ["inf", "part", "ger", "sup"]:
        person = str(person)
        if person not in ["1", "2", "3"]:
            raise ValueError("Invalid person [" + str(person) + "] provided. Choose from: 1, 2, 3")
        if number.lower() not in ["s", "p"]:
            raise ValueError("Invalid number [" + str(number) + "] provided. Choose from: s, p")
        if tense.lower() not in ["pres", "perf", "impf", "fut", "plup", "futp"]:
            raise ValueError("Invalid tense [" + str(tense) + "] provided. Choose from: pres, perf, impf, fut, plup, futp")
        if mood.lower() not in ["ind", "sub", "imp"]:
            raise ValueError("Invalid mood [" + str(mood) + "] provided. Choose from: ind, sub, imp")
        if voice.lower() not in ["act", "pass"]:
            raise ValueError("Invalid voice [" + str(voice) + "] provided. Choose from: act, pass")
        conj = str(person) + "|" + number.lower() + "|" + tense.lower() + "|" + voice.lower() + "|" + mood.lower()
    else:
        if infinites.lower() not in ["ger", "sup"]:
            if tense.lower() not in ["pres", "perf", "fut"]:
                raise ValueError("Invalid tense [" + str(tense) + "] provided for infinitive/participle. Choose from: pres, perf")
            if voice.lower() not in ["act", "pass"]:
                raise ValueError("Invalid voice [" + str(voice) + "] provided for infinitive/participle. Choose from: act, pass")
            conj = tense.lower() + "|" + voice.lower() + "|" + infinites.lower()
        else:
            if infinites.lower() == "ger" and case not in ["gen", "dat", "acc", "abl"]:
                raise ValueError("Invalid case [" + str(case) + "] provided for gerund. Choose from: gen, dat, acc, abl")
            if infinites.lower() == "sup" and case not in ["acc", "abl"]:
                raise ValueError("Invalid case [" + str(case) + "] provided for supine. Choose from: acc, abl")
            conj = case.lower() + "|" + infinites.lower()

    conjs = get_conjug(verb)
    if conj not in conjs:
        return "Conjugation not found for the given verb. Conjugation given: " + conj + ". Conjugations found: " + ", ".join(conjs)
    
    return get_conjug(verb, conj)


def get_word_atts(latin_word, pd=None):
    if pd==None:
        pd = initialize_data()
    c = pd[pd['latin'] == latin_word]
    return [str(a) for a in c['translation']], "verb"

def get_latin_declension_number(latin_word, pd=None):
    if pd==None:
        pd = initialize_data()
    c = pd[pd['latin'] == latin_word]
    return str(c['conjugationType'].iloc[0])


# Main script
def main():
    # Open the existing JSON file
    with open('lat.json', 'r') as file:
        data = json.load(file)

    all_verbs_data = data['verbs']  # Accumulate data here

    # Open file first.txt
    with open("third.txt", "r") as f:
        first = f.readlines()


    start_time = time.time()
    for v in first:
        current_time = time.time()
        # Stop if more than 10 minutes have passed
        if current_time - start_time > 600:
            break

        s = save_info(v.strip(), all_verbs_data)
        # Wait a random time between 5 and 8 seconds
        if s:
            time.sleep(random.randint(5, 8))

    # Write the accumulated data back to the JSON file
    with open('lat.json', 'w') as file:
        json.dump({'verbs': all_verbs_data}, file, indent=4)

# Add comment for pushing more

if __name__ == '__main__':
    main()