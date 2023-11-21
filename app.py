from flask import Flask, render_template, request, session, redirect, url_for
import os
import game
import extract as fetch
import random
import verify
import json
from flask import jsonify

def load_lat_verbs():
    with open('lat.json', 'r') as file:
        data = json.load(file)
    return [verb['latin'] for verb in data['verbs']]

lat_verbs = load_lat_verbs()


app = Flask(__name__)
app.secret_key = 'wowthiskeyisunguessable' 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_conjugation')
def get_conjugation():
    verb = request.args.get('verb')
    tense = request.args.get('tense')
    conjugation = fetch.get_latin_verb_conjugation(verb, conjugation=tense)
    return jsonify({'conjugation': game.demacronize(conjugation)})

@app.route('/get_conjugation_type')
def get_conjugation_type():
    verb = request.args.get('verb')
    conjugation_type = fetch.get_latin_declension_number(verb)
    translations, _ = fetch.get_word_atts(verb)
    meaning = ', '.join(translations)
    return jsonify({'conjugationType': conjugation_type, 'meaning': meaning})


@app.route('/practice', methods=['GET'])
def practice_get():
    if request.method == 'GET':
        # Existing logic to retrieve checkbox values from request.args if present
        # or from the session if not present

        if not session.get('tenserules'):
            session['tenserules'] = [
                ['1', '2', '3'],
                ['s', 'p'],
                ['pres', 'impf', 'fut', 'perf', 'plup', 'futp'],
                ['act', 'pass'],
                ['ind', 'subj', 'inf', 'imp'],
                [''],
                ['nom', 'gen', 'dat', 'acc', 'abl', 'voc']
            ]

        tenserules = [
            request.args.getlist('person') or session.get('tenserules')[0],
            request.args.getlist('number') or session.get('tenserules')[1],
            request.args.getlist('tense') or session.get('tenserules')[2],
            request.args.getlist('voice') or session.get('tenserules')[3],
            request.args.getlist('mood') or session.get('tenserules')[4],
            request.args.getlist('infinites') or session.get('tenserules')[5],
            request.args.getlist('case') or session.get('tenserules')[6],
        ]

        if not session.get('possible_conjugations'):
            session['possible_conjugations'] = ["1", "2", "3", "3io", "4", "dep", "irr", "own"]
        session['possible_conjugations'] = request.args.getlist('conjs') or session.get('possible_conjugations')

        if not request.args.getlist('infinites'):
            tenserules[5] = ['']
        if not request.args.getlist('mood'):
            tenserules[4] = ['']
        if not request.args.getlist('voice'):
            tenserules[3] = ['']
        if not request.args.getlist('case'):
            tenserules[6] = ['nom', 'gen', 'dat', 'acc', 'abl', 'voc']
        if not request.args.getlist('tense'):
            tenserules[2] = ['']
        if not request.args.getlist('number'):
            tenserules[1] = ['']
        if not request.args.getlist('person'):
            tenserules[0] = ['']

        if session['displayCustom']:
            session['displayCustom'] = session['displayCustom']
        else:
            session['displayCustom'] = ""
        custom_verbs = request.args.get('customVerbs')
        if custom_verbs:
            session['customVerbs'] = custom_verbs.splitlines()
            session['illegalCustomVerbs'] = [v for v in session['customVerbs'] if v.lower() not in lat_verbs]
            session['displayCustom'] = '\n'.join(session['customVerbs'])

        # The rest of your logic for handling a GET request

        session['tenserules'] = tenserules
        if 'own' in session.get('possible_conjugations', []):
            print("This is what we got: " + str(session.get('customVerbs', [])))
            print([v.lower() for v in session.get('customVerbs', [])])
            if [v.lower() for v in session.get('customVerbs', [])][0] in lat_verbs:
                print("I can confirm that " + [v.lower() for v in session.get('customVerbs', [])][0] + " is in lat_verbs.")
            vs = [v.lower() for v in session.get('customVerbs', []) if v.lower() in lat_verbs]  # lat_verbs should be loaded from lat.json
            print("this is vs: " + str(vs))
            if len(vs) == 0:
                print("WARNING: No custom verbs left after filtering. Returning all verbs.")
                vs = lat_verbs
        else:
            verbs = game.load_verbs()
            vs = game.filter_verbs(verbs, session['possible_conjugations'])
        session['verb'] = game.get_random_verb(vs)
        print("We got verb " + session['verb'] + ".")
        conjs = fetch.get_conjug(session['verb'])
        filtered_conjs = game.filter_tenses(conjs, tenserules)
        session['tense'] = random.choice(filtered_conjs if filtered_conjs else conjs)
        session['example_sentence'] = game.create_example_sentence(session['tense'])
        return render_template('practice.html', verb=session['verb'], tense=session['tense'], example_sentence=session['example_sentence'])


@app.route('/practice', methods=['POST'])
def practice_post():
    if request.method == 'POST':
        user_input = request.form.get('conjugation')  # Use .get to avoid KeyError
        correct_conjugation = request.form['correctConjugation']
        if correct_conjugation is None or len(correct_conjugation) < 1:
            print("Oopsie woopsie! Seems like the correct conjugation decided to dip for no bloody reason. Let's try again.")
            correct_conjugation = game.demacronize(fetch.get_latin_verb_conjugation(session['verb'], conjugation=session['tense']))
        try_same_verb = 'try_same_verb' in request.form

        result = None
        if user_input is not None:
            if user_input == correct_conjugation:
                result = "Correct! The answer is " + correct_conjugation + "."
            elif verify.damerau_levenshtein_distance(user_input, correct_conjugation) <= 2:
                result = "Close! The correct answer is " + correct_conjugation + "; you typed " + user_input + "."
            else:
                result = "Incorrect! The correct answer is " + correct_conjugation + "; you typed " + user_input + "."

        if try_same_verb:
            # If the user wants to try the same verb
            conjs = fetch.get_conjug(session['verb'])
            filtered_conjs = game.filter_tenses(conjs, session.get('tenserules'))
            session['tense'] = random.choice(filtered_conjs if filtered_conjs else conjs)
            session['example_sentence'] = game.create_example_sentence(session['tense'])
        else:
            # Load new verb and tense
            verbs = game.load_verbs()
            vs = [verb for sublist in verbs for verb in sublist]
            session['verb'] = game.get_random_verb(vs)
            conjs = fetch.get_conjug(session['verb'])
            session['tense'] = random.choice(conjs)
            session['example_sentence'] = game.create_example_sentence(session['tense'])

        return render_template('practice.html', verb=session['verb'], tense=session['tense'], example_sentence=session['example_sentence'], result=result)
    

    # If GET request, set up a new verb and tense
    verbs = game.load_verbs()
    if not session.get('possible_conjugations'):
        session['possible_conjugations'] = ["1", "2", "3", "3io", "4", "dep", "irr"]
    vs = game.filter_verbs(verbs, session['possible_conjugations'])
    session['verb'] = game.get_random_verb(vs)
    conjs = fetch.get_conjug(session['verb'])
    if len(conjs) == 0:
        print("WARNING: No conjugations found for verb " + session['verb'] + ".")
        conjs = ["1|s|pres|act|ind", "2|s|pres|act|ind", "3|s|pres|act|ind", "1|p|pres|act|ind", "2|p|pres|act|ind", "3|p|pres|act|ind"]
    session['tense'] = random.choice(conjs)
    session['example_sentence'] = game.create_example_sentence(session['tense'])
    return render_template('practice.html', verb=session['verb'], tense=session['tense'], example_sentence=session['example_sentence'])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use Heroku's PORT environment variable or 5000 if it's not set
    app.run(host='0.0.0.0', port=port)
    #app.run(debug=True)