import requests
import json
import datetime
from feedgen.feed import FeedGenerator
import requests
from git import Repo

STAGE_FILE='stage.xml'
SALMON_FILE='salmon.xml'

_res = requests.get('https://splatoon3.ink/data/locale/ja-JP.json')
data = json.loads(_res.content)
dict_stages = data['stages']
dict_rules  = data['rules']
dict_weapons = data['weapons']
response = requests.get('https://splatoon3.ink/data/schedules.json')
data = json.loads(response.content)

def stage_schedule():

    dict_result = {}
    is_fes = False

    nawabari = data['data']['regularSchedules']['nodes']
    for item in nawabari:
        try:
            time            = item["startTime"]
            timestamp       = datetime.datetime.fromisoformat(time.rstrip('Z'))
            delta           = datetime.timedelta(hours=9)
            timestamp_local = timestamp + delta
            stage_id1       = item["regularMatchSetting"]["vsStages"][0]["id"]
            stage_id2       = item["regularMatchSetting"]["vsStages"][1]["id"]
            dict_result[timestamp_local] = [f'■ナワバリバトル：{dict_stages[stage_id1]["name"]} / {dict_stages[stage_id2]["name"]}']
        except TypeError:
            is_fes = True

    bankara = data['data']['bankaraSchedules']['nodes']
    for item in bankara:
        try:
            time            = item["startTime"]
            timestamp       = datetime.datetime.fromisoformat(time.rstrip('Z'))
            delta           = datetime.timedelta(hours=9)
            timestamp_local = timestamp + delta
            rule            = item["bankaraMatchSettings"][0]["vsRule"]["id"]
            stage_id1       = item["bankaraMatchSettings"][0]["vsStages"][0]["id"]
            stage_id2       = item["bankaraMatchSettings"][0]["vsStages"][1]["id"]
            dict_result[timestamp_local].append(f'■チャレンジ({dict_rules[rule]["name"]})：{dict_stages[stage_id1]["name"]} / {dict_stages[stage_id2]["name"]}')
        except TypeError:
            is_fes = True

    bankara = data['data']['bankaraSchedules']['nodes']
    for item in bankara:
        try:
            time            = item["startTime"]
            timestamp       = datetime.datetime.fromisoformat(time.rstrip('Z'))
            delta           = datetime.timedelta(hours=9)
            timestamp_local = timestamp + delta
            rule            = item["bankaraMatchSettings"][1]["vsRule"]["id"]
            stage_id1       = item["bankaraMatchSettings"][1]["vsStages"][0]["id"]
            stage_id2       = item["bankaraMatchSettings"][1]["vsStages"][1]["id"]
            dict_result[timestamp_local].append(f'■オープン({dict_rules[rule]["name"]})：{dict_stages[stage_id1]["name"]} / {dict_stages[stage_id2]["name"]}')
        except TypeError:
            is_fes = True

    x_match = data['data']['xSchedules']['nodes']
    for item in x_match:
        try:
            time            = item["startTime"]
            timestamp       = datetime.datetime.fromisoformat(time.rstrip('Z'))
            delta           = datetime.timedelta(hours=9)
            timestamp_local = timestamp + delta
            rule            = item["xMatchSetting"]["vsRule"]["id"]
            stage_id1       = item["xMatchSetting"]["vsStages"][0]["id"]
            stage_id2       = item["xMatchSetting"]["vsStages"][1]["id"]
            dict_result[timestamp_local].append(f'■Xマッチ({dict_rules[rule]["name"]})：{dict_stages[stage_id1]["name"]} / {dict_stages[stage_id2]["name"]}')
        except TypeError:
            is_fes = True

    if is_fes:
        fest = data['data']['festSchedules']['nodes']
        for item in fest:
            try:
                time            = item["startTime"]
                timestamp       = datetime.datetime.fromisoformat(time.rstrip('Z'))
                delta           = datetime.timedelta(hours=9)
                timestamp_local = timestamp + delta
                stage_id1       = item["festMatchSetting"]["vsStages"][0]["id"]
                stage_id2       = item["festMatchSetting"]["vsStages"][1]["id"]
                dict_result[timestamp_local] = [f'■フェスマッチ：{dict_stages[stage_id1]["name"]} / {dict_stages[stage_id2]["name"]}']
            except TypeError:
                pass

    return dict_result

def salmon_schedule():
    salmon = data['data']['coopGroupingSchedule']['regularSchedules']['nodes']
    dict_result = {}
    for item in salmon:
        weapons = []
        time            = item["startTime"]
        timestamp       = datetime.datetime.fromisoformat(time.rstrip('Z'))
        delta           = datetime.timedelta(hours=9)
        timestamp_local = timestamp + delta
        stage_id        = item["setting"]["coopStage"]["id"]
        for weapon in item["setting"]['weapons']:
            weapons.append('・' + dict_weapons[weapon['__splatoon3ink_id']]['name'])
        dict_result[timestamp_local] = f'■{dict_stages[stage_id]["name"]}' + '\n' + '\n'.join(weapons)

    return dict_result

def git_push():
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    repo = Repo()
    repo.git.commit('.','-m','\"' + now +'\"')
    origin = repo.remote(name='origin')
    origin.push()

if __name__ == '__main__':

    # Stage schedule
    res = stage_schedule()
    dict_entry = {}

    for k in reversed(res):
        dict_entry[k] = k.strftime('%Y/%m/%d %H:%M') + '〜'
        for item in res[k]:
            dict_entry[k] = dict_entry[k] + '\n' + item

    fg = FeedGenerator()
    fg.title('My RSS feed')
    fg.description('This is an example RSS feed')
    fg.link(href='https://splatoon3.ink', rel='alternate')

    num = 1
    for k in dict_entry:
        fe = fg.add_entry()
        fe.id('http://example.com/entries/' + str(num))
        fe.title(dict_entry[k])
        fe.link(href='https://splatoon3.ink', rel='alternate')
        fe.description('')
        fe.pubDate(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'))
        num = num + 1

    xml_str = fg.rss_str(pretty=True)
    with open(STAGE_FILE, 'wb') as f:
        f.write(xml_str)
    
    #Salmonrun schedule
    res = salmon_schedule()
    dict_entry = {}

    for k in reversed(res):
        dict_entry[k] = k.strftime('%Y/%m/%d %H:%M') + '〜'
        for item in res[k]:
            dict_entry[k] = dict_entry[k] + item

    fg = FeedGenerator()
    fg.title('My RSS feed')
    fg.description('This is an example RSS feed')
    fg.link(href='https://splatoon3.ink', rel='alternate')

    num = 1
    for k in dict_entry:
        fe = fg.add_entry()
        fe.id('http://example.com/entries/' + str(num))
        fe.title(dict_entry[k])
        fe.link(href='https://splatoon3.ink', rel='alternate')
        fe.description('')
        fe.pubDate(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'))
        num = num + 1

    xml_str = fg.rss_str(pretty=True)
    with open(SALMON_FILE, 'wb') as f:
        f.write(xml_str)

    git_push()