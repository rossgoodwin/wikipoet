import re
import random
import requests
import nltk
from nltk.corpus import wordnet as wn


s = requests.Session()
a = requests.adapters.HTTPAdapter(max_retries=5)
s.mount('http://', a)


_digits = re.compile('\d')
def contains_digits(d):
    """If input string contains digits, returns True"""
    return bool(_digits.search(d))


def pwords(word, text):
    """Takes in word and article text and returns candidate adjectives and nouns"""
    tokens = nltk.word_tokenize(text)
    t_pos = nltk.pos_tag(tokens)
    aw = ['JJ', 'JJR', 'JJS', 'NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
    words = [i for i in t_pos if i[1] in aw]
    prox_word = [i[0].lower() for i in words if wn.synsets(i[0].lower(), pos='a') or wn.synsets(i[0].lower(), pos='n')]
    prox_word = list(set(prox_word))
    adj = []
    noun = []
    for i in prox_word:
        ss_a = wn.synsets(i, pos='a')
        ss_n = wn.synsets(i, pos='n')
        for xa in ss_a:
            adj += xa.lemma_names
        for xn in ss_n:
            noun += xn.lemma_names
    for i in range(len(adj)):
        adj[i] = adj[i].lower()
        if '_' in adj[i]:
            sp = adj[i].split('_')
            sj = ' '.join(sp)
            adj[i] = sj
        else:
            pass
    for j in range(len(noun)):
        noun[j] = noun[j].lower()
        if '_' in noun[j]:
            tp = noun[j].split('_')
            tj = ' '.join(tp)
            noun[j] = tj
        else:
            pass
    adj = list(set(adj))
    noun = list(set(noun))
    for i in adj[:]:
        if contains_digits(i) or len(i) < 3 or i == word:
            adj.remove(i)
        else:
            pass
    for i in noun[:]:
        if contains_digits(i) or len(i) < 3 or i == word:
            noun.remove(i)
        else:
            pass
    return [adj, noun]


def checker(word, x):
    """Checks candidate words by searching Wikipedia for cases in which they are used alongside the original word"""
    y = x[0]
    z = x[1]
    url = 'http://en.wikipedia.org/w/api.php'
    headers = {'User-Agent': 'SmartWriter/0.1 (http://rossgoodwin.com; ross.goodwin@gmail.com)'}
    for i in y[:]:
        search_string = "\"" + i + ' ' + word + "\""
        payload = {'action': 'query', 'list': 'search', 'format': 'json', 'srsearch': search_string, 
                   'srlimit': 1, 'srprop': 'snippet', 'srwhat': 'text'}
        r = s.get(url, params=payload, headers=headers)
        json_obj = r.json()
        hits = int(json_obj['query']['searchinfo']['totalhits'])
        if hits < 10:
            y.remove(i)
        else:
            pass
    for i in z[:]:
        search_string = "\"" + word + ' ' + i + "\""
        payload = {'action': 'query', 'list': 'search', 'format': 'json', 'srsearch': search_string, 
                   'srlimit': 1, 'srprop': 'snippet', 'srwhat': 'text'}
        r = s.get(url, params=payload, headers=headers)
        json_obj = r.json()
        hits = int(json_obj['query']['searchinfo']['totalhits'])
        if hits < 10:
            z.remove(i)
        else:
            pass
    return [y, z]
        

def article_fetcher(word):
    """Fetches article, runs pwords on article text and checker on candidate words, returns final word lists"""
    url = 'http://en.wikipedia.org/w/api.php'
    payload = {'format': 'json', 'action': 'query', 'titles': word, 'prop': 'extracts', 'explaintext': 1}
    headers = {'User-Agent': 'SmartWriter/0.1 (http://rossgoodwin.com; ross.goodwin@gmail.com)'}
    r = s.get(url, params=payload, headers=headers)
    json_obj = r.json()
    try:
        text = json_obj['query']['pages'].values()[0]['extract']
    except KeyError:
        op2 = False
    else:
        op1 = pwords(word, text)
        op2 = checker(word, op1)
    return op2


def poet(word, desc):
    """Assembles stanza, finds next word, assembles next stanza, lather, rinse, repeat"""
    for _ in range(10):
        if desc and len(desc[0]) >= 10 and len(desc[1]) >= 7:
            adj = desc[0]
            noun = desc[1]
            a = random.sample(adj, 10)
            n = random.sample(noun, 7)
            print word
            print a[0] + ' ' + word
            print a[1] + ', ' + a[2] + ' ' + word
            print a[3] + ', ' + a[4] + ', ' + a[5] + ' ' + word
            print a[6] + ', ' + a[7] + ', ' + a[8] + ', ' + a[9] + ' ' + word
            print word + ' ' + n[0] + ', ' + word + ' ' + n[1] + ', ' + word + ' ' + n[2]
            print word + ' ' + n[3] + ', ' + word + ' ' + n[4] + ', ' + word + ' ' + n[5]
            new_word = n[6]
            new_desc = article_fetcher(new_word)
            if (not new_desc) or len(new_desc[0]) < 10 or len(new_desc[1]) < 7:
                random.shuffle(noun)
                for i in noun:
                    new_word = i
                    new_desc = article_fetcher(new_word)
                    if new_desc and len(new_desc[0]) >= 10 and len(new_desc[1]) >= 7:
                        break
                    else:
                        continue
            else:
                pass
            print word + ' ' + new_word
            word = new_word
            desc = new_desc
        else:
            break
    print "\n\n ~wikipoet"


def main(word):
    """Generates simple poem from a word using Wikipedia"""
    desc = article_fetcher(word)
    poet(word, desc)


if __name__ == "__main__":
    w = raw_input('starting word >> ')
    main(w)