
import os
import random
import fetch

# Get path to current directory
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

def load_verbs():
    # Open first.txt, firstdep.txt, second.txt, seconddep.txt, third.txt, thirddep.txt, fourth.txt, fourthdep.txt
    # and read all the lines
    verbs = []
    files = ['first.txt', 'firstdep.txt', 'second.txt', 'seconddep.txt', 'third.txt', 'thirddep.txt', 'thirdio.txt', 'fourth.txt', 'fourthdep.txt', "irregular.txt", "ownverbs.txt"]
    for file in files:
        with open(os.path.join(BASE_PATH, file), 'r') as f:
            v = []
            v += f.read().splitlines()
            verbs.append(v)
    # Return a list of all the verbs
    return verbs

def filter_verbs(verbs, possible_conjugations):
    totverbs = []
    if "1" in possible_conjugations:
        totverbs += verbs[0]
    if "2" in possible_conjugations:
        totverbs += verbs[2]
    if "3" in possible_conjugations:
        totverbs += verbs[4]
    if "3io" in possible_conjugations:
        totverbs += verbs[6]
    if "4" in possible_conjugations:
        totverbs += verbs[7]
    if "dep" in possible_conjugations:
        totverbs += verbs[1] + verbs[3] + verbs[5] + verbs[8]
    if "irr" in possible_conjugations:
        totverbs += verbs[9]
    if "own" in possible_conjugations:
        totverbs += verbs[10]
    if len(totverbs) == 0:
        print("WARNING: No verbs left after filtering. Returning all verbs.")
        return [verb for sublist in verbs for verb in sublist]
    return totverbs


def get_random_verb(verbs):
    return random.choice(verbs)


tenserules = [
    ["1", "2", "3"],
    ["s", "p"],
    ["pres", "impf", "fut", "perf", "plup", "futp"],
    ["act", "pass", "imp"],
    ["ind", "sub", "imp"],
    ["sup", "ger", "inf", "part"],
    ["acc", "abl", "dat", "gen"]
]

def filter_tenses(possible_tenses, tenserules):
    # Filter out tenses that are not in the rules
    newtenses = []
    print(tenserules)
    for tense in possible_tenses:
        if "aor" in tense or "sigm" in tense:
            continue
        t = tense.split("|")
        if t[0] in tenserules[0] and t[1] in tenserules[1] and t[2] in tenserules[2] and t[3] in tenserules[3] and t[4] in tenserules[4]:
            newtenses.append(tense)
        elif t[0] in tenserules[2] and t[1] in tenserules[3] and t[2] in tenserules[5]:
            newtenses.append(tense)
        elif t[0] in tenserules[6] and t[1] in tenserules[5]:
            newtenses.append(tense)
    if len(newtenses) == 0:
        print("WARNING: No tenses left after filtering. Returning all tenses.")
        return possible_tenses
    return newtenses
    
def create_example_sentence(conjugation):
    # Conjugation is on the form "num|pers|tense|voice|mood"
    if len(conjugation.split("|")) == 5 and "imp" not in conjugation.split("|"):
        print(conjugation, "Conjugtaion")
        s = ""
        tense = {
            "pres": "nunc",
            "impf": "Antea saepius",
            "fut": "cras",
            "perf": "heri",
            "plup": "ante hoc factum est,",
            "futp": "ante hoc futurus sit,"
        }
        person = {
            "1": ["ego", "nos"],
            "2": ["tu", "vos"],
            "3": ["is", "ii"]
        }
        mood = {
            "ind": "",
            "sub": "utinam",
            "subj": "utinam",
        }
        voice = {
            "act": "",
            "pass": "a aliquo",
        }

        conj = conjugation.split("|")
        if len(conj) != 5:
            return "Not implemented for this conjugation"
        s += tense[conj[2]] + " "
        if conj[1] == "s":
            s += person[conj[0]][0] + " "
        else:
            s += person[conj[0]][1] + " "
        s += mood[conj[4]] + " "
        s += "--- "
        s += voice[conj[3]] + " "

        return s
    elif "imp" in conjugation.split("|"):
        s = "Heus "
        person = {
            "2": ["tu", "vos"],
            "3": ["is", "ii"]
        }
        tense = {
            "pres": "Nunc",
            "fut": "Cras",
        }
        voice = {
            "act": "",
            "pass": "a aliquo",
        }

        conj = conjugation.split("|")
        if conj[1] == "s":
            s += person[conj[0]][0] + "! "
        else:
            s += person[conj[0]][1] + "! "
        s += tense[conj[2]] + " "
        s += "--- "
        s += voice[conj[3]] + "! Sic impero!"
        return s

    elif len(conjugation.split("|")) == 3:
        if conjugation == "pres|act|inf":
            s = "Puto eum nunc ---"
        elif conjugation == "pres|act|part":
            s = "Id nunc facio ---"
        elif conjugation == "perf|act|inf":
            s = "Puto eum heri ---"
        elif conjugation == "pres|pass|inf":
            s = "Puto eum nunc --- a aliquo"
        elif conjugation == "perf|pass|inf":
            s = "Puto eum heri --- a aliquo"
        elif conjugation == "perf|pass|part":
            s = "Is a me --- est"
        else:
            s = "Not implemented for this conjugation"
        return s
    elif len(conjugation.split("|")) == 2:
        if conjugation == "gen|ger":
            s = "Ars --- pulcherrima est"
        elif conjugation == "dat|ger":
            s = "Credo ---"
        elif conjugation == "abl|ger":
            s = "Utor ---"
        elif conjugation == "acc|ger":
            s = "Venio ad ---"
        elif conjugation == "acc|sup":
            s = "--- eo."
        elif conjugation == "abl|sup":
            s = "Non est facilis ---"
        else:
            s = "Not implemented for this conjugation"
        return s
    return "Not implemented for this conjugation"





def demacronize(word):
    return word.replace('ā', 'a').replace('ē', 'e').replace('ī', 'i').replace('ō', 'o').replace('ū', 'u')
    

if __name__ == "__main__":
    verbs = load_verbs()
    vs = []
    for i in verbs:
        vs += i
    

    while True:
        v = get_random_verb(vs)
        conjs = fetch.get_conjug(v)
        randconj = random.choice(conjs)
        print("Please conjugate the verb: " + v + " in the " + randconj + " tense.")
        print("Example sentence: " + create_example_sentence(randconj))
        a = input("Enter your answer: ")

        if a == demacronize(fetch.get_latin_verb_conjugation(v, conjugation=randconj)):
            print("Correct!")
        else:
            print("NO! Correct answer is " + demacronize(fetch.get_latin_verb_conjugation(v, conjugation=randconj)))
        print("--------------------")