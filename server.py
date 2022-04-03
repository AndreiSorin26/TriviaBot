# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import json

import requests
import re
from bs4 import BeautifulSoup
import pycountry
import pandas as pd
import flask
import unidecode
from flask import jsonify, request

app = flask.Flask(__name__)
app.config["DEBUG"] = True

uselessStrings = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
                  "november", "december",
                  "the", "republic", "from", "for", "in", "of", 'at', 'below', 'after', 'before', "winter", "summer",
                  "autumn", "spring",
                  "ocean", "river", "sea", "lake", "city", "country", "planet", "channel", "empire"]

listele = ["greatest", "largest", "biggest", "fastest", "best", "tallest", "scariest", "most"]
orderererere = ["first", "second", "third", "forth", "fifth", "sixth", "seventh", "eighth", "ninth"]
verbele = ["is", "are", "were", "was", "have", "has", "had", "will", "titled", "released"]


def search_urls(query):
    try:
        from googlesearch import search
    except ImportError:
        print("No module named 'google' found")

    # to search

    urls = []
    for j in search(query, tld="co.in", num=10, stop=10, pause=2):
        if "images" not in j:
            urls.append(j)

    return urls


def check_numeric(text):
    match = re.match("^[1-9]{1,4}$", text)
    if match is not None:
        return True
    return False


def is_punctuation(word):
    a = [".", ",", ";", "?", "!"]
    if word in a:
        return True
    return False


def parse_years(text):
    words = re.split("[ ,.)(]", text)
    years = []
    for i in range(len(words)):
        if check_numeric(words[i]) and not is_punctuation(words[i + 1]) and (
                int(words[i]) > 31 or words[i + 1] == 'AD' or words[i + 1] == 'BC'):
            years.append(words[i])

    return years


def arr_in_str(v, str):
    for x in v:
        if x in str:
            return True
    return False


def when_question(question):
    urls = search_urls(question)
    urls = list(filter(lambda x: "history" not in x, urls))
    mapp = {}
    for url in urls:
        content = requests.get(url).text
        if "<body" in content:
            content = content[content.find("<body"): (content.find("</body>") + 7)]
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.get_text(" ")
            content = re.sub(r'[\n]', "", content)
            years = parse_years(content)

            for year in years:
                if year not in question:
                    if year in mapp.keys():
                        mapp[year] += 1
                    else:
                        mapp[year] = 1

    max_val = list(mapp.keys())[0]
    for key in mapp.keys():
        if mapp[key] > mapp[max_val]:
            max_val = key

    return max_val


def parse_names(text):
    words = re.split("[ .]", text)
    words = list(filter(lambda x: len(x) > 1, words))
    persons = []
    i = 0
    while i < len(words):
        if words[i][0].isupper():
            j = i + 1
            full_name = words[i]
            aux = 0
            while j < len(words) and (words[j][0].isupper() or words[j].lower() in ["of", "de", "for"]) and aux < 2:
                full_name += " " + words[j]
                j += 1
                i += 1
                aux += 1

            for name in re.split("[,;!?.\n]", full_name):
                if len(name) > 2 and name.lower() not in uselessStrings:
                    persons.append(name)
        i += 1
    return persons


def not_a_country(str):
    for country in pycountry.countries:
        if country.name.lower() == str.lower():
            return False
    return True


def who_question(question):
    urls = search_urls(question)
    mapp = {}
    for url in urls:
        content = requests.get(url).text
        if "<body" in content:
            content = content[content.find("<body"): (content.find("</body>") + 7)]
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.get_text(" ")
            content = re.sub(r'[\n.:!?,;)(]{1,100}', " ", content)
            content = unidecode.unidecode(content)
            persons = parse_names(content)
            for person in persons:
                if person.lower() not in question.lower() and not_a_country(person):
                    if person in mapp.keys():
                        mapp[person] += 1
                    else:
                        mapp[person] = 1

    max_val = list(mapp.keys())[0]
    for key in mapp.keys():
        if mapp[key] > mapp[max_val]:
            max_val = key

    return max_val


def add_to_map(map, value):
    if value in map.keys():
        map[value] += 1
    else:
        map[value] = 1


def parse_places(text):
    places = []
    words = re.split("[ ,.]", text)
    for i in range(2, len(words)):
        if words[i - 2] in ["from", "in", "at", "the", "to"] and len(words[i]) > 0 and words[i][0].isupper():
            places.append(words[i])
        elif words[i - 1] in ["from", "in", "at", "the", "to"] and len(words[i]) > 0 and words[i][0].isupper():
            places.append(words[i])

    return places


def where_question(question):
    urls = []
    if "from" not in question:
        urls = search_urls(question + " from")
    else:
        urls = search_urls(question)

    mapp = {}
    for url in urls:
        content = requests.get(url).text
        if "<body" in content:
            content = content[content.find("<body"): (content.find("</body>") + 7)]
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.get_text(" ")
            content = re.sub(r'[\n.:!?,;)(]{1,100}', "", content)

            for country in pycountry.countries:
                if country.name in content or country.alpha_2 in content or country.alpha_3 in content:
                    if country.name in mapp.keys():
                        mapp[country.name] += 1
                    else:
                        mapp[country.name] = 1

    max_val = list(mapp.keys())[0]
    for key in mapp.keys():
        if mapp[key] > mapp[max_val]:
            max_val = key

    return max_val


def remove_first_two_words(str):
    words = re.split(" ", str)
    return ' '.join(words[2:])


def find_nth(string, substr, n):
    start = string.find(substr)
    while start >= 0 and n > 1:
        start = string.find(substr, start + len(substr))
        n -= 1
    return start


def exists_crt_column(table):
    for i in range(len(table)):
        if not str(table.iloc[i, 0]).isnumeric():
            return False
    return True


def what_questions(question, question_type):
    get_top = False
    for word in question.split(" "):
        if word in listele:
            question += " list of"
            get_top = True
    if question_type == "Gaming":
        question += " fandom"

    if get_top:
        urls = search_urls(question)
        urls = list(filter(lambda x: "wikipedia" in x, urls))
        for url in urls:
            content = requests.get(url).text
            if "<body" in content:
                content = content[content.find("<body"): (content.find("</body>") + 7)]
                times = -1
                for word in question.split(" "):
                    if word.lower() in orderererere:
                        times = orderererere.index(word.lower())

                soup = BeautifulSoup(content, 'html.parser')
                indiatable = soup.find('table', {'class': "wikitable"})
                df = pd.read_html(str(indiatable))
                df = pd.DataFrame(df[0])

                aux = 1
                if "Rank" in df.columns:
                    aux = 0

                if times != -1:
                    return str(df.iloc[times, 1 - aux])
                else:
                    return str(df.iloc[0, 1 - aux])

    if question_type == "Geography":
        return where_question(question)

    if question_type == "Music" and "instrument" in question:
        urls = search_urls(question)
        urls = list(filter(lambda x: "wikipedia" in x, urls))
        for url in urls:
            content = requests.get(url).text
            if "<body" in content:
                content = content[content.find("<body"): (content.find("</body>") + 7)]
                soup = BeautifulSoup(content, 'html.parser')
                indiatable = soup.find('table', {'class': "wikitable"})
                df = pd.read_html(str(indiatable))
                df = pd.DataFrame(df[0])

                for i in len(df):
                    if df.iloc[i, 0] == "Instrument":
                        return df.iloc[i, 1]

    if question.split(" ")[1] in verbele:
        return who_question(" ".join(question.split(" ")[2:]))

    urls = search_urls(question)
    for url in urls:
        content = requests.get(url).text
        if "<body" in content:
            content = content[content.find("<body"): (content.find("</body>") + 7)]
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.get_text(" ")

            words = content.split(" ")
            strr = ""
            for i in range(len(words)):
                if words[i] == question.split(" ")[2] and words[i] not in question:
                    count = 0
                    while count < 10:
                        if i - count >= 0 and words[i - count] in question:
                            strr += word[i - count]
                    if strr == "":
                        count = 0
                        while count < 10:
                            if i + count < len(words) and words[i + count] in question:
                                strr += word[i + count]

            return strr


def parse_numbers(text):
    return re.findall(r'[0-9]{1,100}', text)


def multiple_choice(question, choices, answer_type):
    urls = search_urls(question)
    mapp = {}
    for choice in choices:
        mapp[choice] = 0

    for url in urls:
        content = requests.get(url).text
        if "<body" in content:
            content = content[content.find("<body"): (content.find("</body>") + 7)]
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.get_text(" ")
            content = re.sub(r'[\n.:!?,;)(]{1,100}', "", content)

            if answer_type == "numeric":
                for choice in choices:
                    if choice in parse_numbers(content):
                        mapp[choice] += 1
            else:
                for choice in choices:
                    if choice in content:
                        mapp[choice] += 1

    max_val = list(mapp.keys())[0]
    for key in mapp.keys():
        if mapp[key] > mapp[max_val]:
            max_val = key

    return max_val

@app.route('/sanity', methods=['GET'])
def check_sanity():
    response = jsonify({
        "status": "ok"
    })
    response.status_code = 200
    return response

@app.route('/question', methods=['POST'])
def question():
    question_contents = request.get_json()
    answer = ""
    print(str(question_contents))
    try:
        if question_contents["question_type"] == "multiple_choice":
            answer = multiple_choice(question_contents["question_text"], question_contents["answer_choices"],
                                     question_contents["answer_type"])
        else:
            question_text = question_contents["question_text"]
            wh_word = question_text.split(" ")[0]
            if wh_word == "What" or wh_word == "Which":
                answer = what_questions(question_text, question_contents["question_type"])
            elif wh_word == "When":
                answer = when_question(question_text)
            elif wh_word == "Who":
                answer = who_question(question_text)
            else:  # wh_word == "Where":
                answer = where_question(question_text)
    except:
        answer = "ERROR ChilotiCuGluga: Sorry :(("

    answer = jsonify({
        "answer": answer
    })
    answer.status_code = 200
    return answer


app.run(port=3000, host="0.0.0.0")
