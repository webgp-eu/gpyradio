import requests
import argparse
import sys
import subprocess

limit = 10
headers = {'user-agent': 'TEST:webgp.eu-gpyradio/0.9'}
player = 'mplayer' # 'mpv'

def search(pattern):
    pattern = pattern.replace(' ', '%20').strip('"');
    r = requests.get('http://www.radio-browser.info/webservice/json/stations/byname/{}'.format(pattern), headers=headers);
    radios = r.json()
    ids = []
    for radio in radios:
        ids.append({'id': radio['id'], 'name': radio['name']})
    return ids

def play(id_radio):
    r = requests.get('http://www.radio-browser.info/webservice/v2/json/url/{}'.format(id_radio), headers=headers)
    radio = r.json()
    if radio['ok'] == "true":
        print('Now playing...', radio['name'])
        subprocess.run([player, radio['url']])
    else:
        print('Error...Radio station not found')
        sys.exit()

def menu(ids, page, start, end, total_pages):
    result = ''
    length = len(ids)
    for i, radio in enumerate(ids[start: end]):
        stri = "{}. {}\n".format(start + i + 1, radio['name'])
        result += stri 
    result += "Radios {}-{} of {}".format(start + 1, end, length)
    options = []
    if page < total_pages:
        options.append("(n)ext page") 
    if page > 0:
        options.append("(p)revious page")
    options.append("(q)uit")
    options_stri = ",".join(options)
    txt = "Choose a radio to stream:"
    txt += "({}) : ".format(options_stri)
    print(result)
    return input(txt)


parser = argparse.ArgumentParser()
# commands search, play ?
parser.add_argument('pattern')
#options: radio id, search terms


args = parser.parse_args()
pattern = args.pattern

ids = search(pattern)
length = len(ids)
total_pages = length // limit 
page = 0
while True:
    if length == 0:
        print("No results. Exiting...")
        sys.exit()
    if length < page * limit:
        page -= 1
        print("Already on last page\n")
    elif page < 0:
        page = 0
        print("Already on first page\n")
    start = page * limit
    end = min((page + 1) * limit, length)
    
    num = menu(ids, page, start, end, total_pages)
    if num == "n":
        page += 1
        continue
    if num == "p":
        page -= 1
        continue
    if num == "q":
        print("Bye bye")
        sys.exit()
    try:
        play(ids[int(num) - 1]['id'])
    except KeyboardInterrupt:
        print("Bye bye")
    except (IndexError, ValueError):
        continue

