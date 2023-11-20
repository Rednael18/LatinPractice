import requests
from bs4 import BeautifulSoup

def get_latin_noun_declension(noun, case, number="Singular", retalts=False):
    # Normalize the case to match the website's format
    case = case.lower().capitalize()

    
    # Make sure the input case is valid for Latin
    valid_cases = ["Nominative", "Genitive", "Dative", "Accusative", "Ablative", "Vocative", "Locative"]
    if case not in valid_cases:
        raise ValueError("Invalid case [" + str(case) + "] provided. Choose from: " + ", ".join(valid_cases))
    
    # Construct the URL
    url = f"https://en.wiktionary.org/wiki/{noun}#Latin"
    
    # Get the page content
    response = requests.get(url)
    response.raise_for_status()  # Raises HTTPError if the HTTP request returned an unsuccessful status code
    
    # Parse the HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the declension table
    tables = soup.find_all('table', class_='inflection-table')
    latin_table = None
    for table in tables:
        if 'inflection-table-la' in table.get('class', []):
            latin_table = table
            break
    
    if not latin_table:
        return "Declension table not found for the given noun."
    
    # Find the requested case
    declension = ""
    alldeclensions = []
    for row in latin_table.find_all('tr'):
        cells = row.find_all('td')
        # Check for headers in the first column and match the requested case
        if cells and str(list(cells)[0])[56:59] == case.lower()[:3]:
            if len(cells[number.lower()=="plural"].findChildren('a')) > 1:
                for i in range(len(cells[number.lower()=="plural"].findChildren('a'))):
                    alldeclensions.append(cells[number.lower()=="plural"].findChildren('a')[i].get_text(strip=True))
            else:
                declension = cells[number.lower()=="plural"].get_text(strip=True)  # Assume singular is in the second cell
            break
    
    if declension:
        return declension
    elif len(alldeclensions) > 0:
        if retalts:
            return alldeclensions
        else:
            return alldeclensions[0]
    else:
        return f"The noun in the {case} case was not found."


def get_conjug(verb, conj=None):
    verb = verb.lower()

    # Construct the URL
    url = f"https://en.wiktionary.org/wiki/{verb}#Latin"
    
    # Get the page content
    response = requests.get(url)
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
        return "Conjugation table not found for the given verb."
    
    conjs = []
    for row in latin_table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) > 1:
            for i in range(len(list(cells))):
                textcont = str(list(cells)[i])
                # If textcont contains "form-of lang-la", print textcont
                if "form-of lang-la" in textcont:
                    # Print the text between "form-of lang-la" and "-form-of"
                    text = textcont[textcont.find("form-of lang-la")+16:textcont.find("-form-of")]
                    if conj is None:
                        if text is not None:
                            if cells[i].get_text(strip=True) != "—":
                                conjs.append(text)
                    else:
                        if text == conj:
                            cnt = cells[i].get_text(strip=True)
                            if "," in cnt:
                                cnt = cnt[:cnt.find(",")]
                            return cnt
        longcells = row.find_all('th')
        if len(longcells) > 1:
            for i in range(len(list(longcells))):
                if longcells[i].get('colspan') == '6':
                    cont = longcells[i].get_text(strip=True)
                    if "present active indicative ofsum" in cont:
                        if conj is None:
                            conjs.append("1|s|perf|pass|ind")
                        elif conj == "1|s|perf|pass|ind":
                            return cont[:cont.find("+ present active indicative ofsum")] + " sum"
                    if "imperfect active indicative ofsum" in cont:
                        if conj is None:
                            conjs.append("1|s|plup|pass|ind")
                        elif conj == "1|s|plup|pass|ind":
                            return cont[:cont.find("+ imperfect active indicative ofsum")] + " eram"
                    if "future active indicative ofsum" in cont:
                        if conj is None:
                            conjs.append("1|s|futp|pass|ind")
                        elif conj == "1|s|futp|pass|ind":
                            return cont[:cont.find("+ future active indicative ofsum")] + " ero"
                    if "present active subjunctive ofsum" in cont:
                        if conj is None:
                            conjs.append("1|s|perf|pass|sub")
                        elif conj == "1|s|perf|pass|sub":
                            return cont[:cont.find("+ present active subjunctive ofsum")] + " sim"
                    if "imperfect active subjunctive ofsum" in cont:
                        if conj is None:
                            conjs.append("1|s|plup|pass|sub")
                        elif conj == "1|s|plup|pass|sub":
                            return cont[:cont.find("+ imperfect active subjunctive ofsum")] + " essem"
    return conjs


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


def get_word_atts(latin_word):
    # Construct the URL to the Wiktionary page for the given word
    url = f"https://en.wiktionary.org/wiki/{latin_word}#Latin"

    # Make a GET request to fetch the page content
    response = requests.get(url)
    translations = []
    wordclass = None

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

    return translations, wordclass[:-6]


def get_latin_declension_number(verb):
    verb = verb.lower()

        # Construct the URL to the Wiktionary page for the given word
    url = f"https://en.wiktionary.org/wiki/{verb}#Latin"

    # Make a GET request to fetch the page content
    response = requests.get(url)

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
                    if currtag.find_next_sibling("h4"):
                        if currtag.find_previous_sibling("h2").get_text() == "Latin[edit]":
                            currtag = currtag.find_next_sibling("h4")
                        else:
                            print("No Latin section found for verb " + verb)
                            stop = True
                    else:
                        print("No Latin section found for verb " + verb)
                        stop = True
            conjtag = currtag.find_next_sibling("table").find("th").get_text()
            if "first" in conjtag:
                return "1"
            elif "second" in conjtag:
                return "2"
            elif "third" in conjtag:
                if "iō-variant" in conjtag:
                    return "3io"
                else:
                    return "3"
            elif "fourth" in conjtag:
                return "4"
            elif "irregular" in conjtag:
                return "irreg"
            else:
                print("No Latin section found for verb " + verb)
        else:
            print("No Latin section found for verb " + verb)
    else:
        print(f"Error fetching the page: {response.status_code}")



#---------------------------------------------

import bz2
from lxml import etree

def extract_page_html(dump_path, page_title):
    print("Beginning extraction of page '" + page_title + "' from dump '" + dump_path + "'.")
    with bz2.open(dump_path, "r") as file:
        print("File opened.")
        context = etree.iterparse(file, events=("end",), tag="{http://www.mediawiki.org/xml/export-0.10/}page")
        print("Context created.")
        
        for event, elem in context:
            print("Event found.")
            title_elem = elem.find("{http://www.mediawiki.org/xml/export-0.10/}title")
            if title_elem is not None and title_elem.text == page_title:
                print("Page found.")
                revision = elem.find("{http://www.mediawiki.org/xml/export-0.10/}revision")
                if revision is not None:
                    print("Revision found.")
                    text_elem = revision.find("{http://www.mediawiki.org/xml/export-0.10/}text")
                    if text_elem is not None and text_elem.text is not None:
                        return text_elem.text
            elem.clear()
        return None

# Replace 'enwiktionary-20231101-pages-meta-current.xml.bz2' with your file path
# Replace 'fumo' with the page title you want to extract
html_content = extract_page_html('enwiktionary-20231101-pages-meta-current.xml.bz2', 'fumo')

if html_content:
    print(html_content)
else:
    print("Page not found.")
