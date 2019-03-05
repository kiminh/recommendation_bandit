# import googleapiclient.discovery
import random
from google.appengine.ext import ndb
from random import randint
from datetime import datetime
import json

AGES = ['0-14', '14-18', '18-25', '25-30', '30-35', '35-40', '40-50', '50-100']
GENDER = ['M', 'F']
REGION = ['NSW', 'ACT', 'QLD', 'VIC', 'SA', 'NT', 'WA', 'TAS']

# PROJECT_ID = 'CPJ Team'
# MODEL_NAME = 'better-classifier'
# VERSION_NAME = '1.1'
#
# service = googleapiclient.discovery.build('ml', 'v1')
# name = 'projects/{}/models/{}/versions/{}'.format(PROJECT_ID, MODEL_NAME, VERSION_NAME)


class Content(ndb.Model):
    """Models an individual Guestbook entry with content and date."""
    content = ndb.TextProperty()
    parameters = ndb.TextProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    url = ndb.StringProperty(indexed=True)

    @classmethod
    def query_content(cls, key):
        return cls.query(cls.url == key)

    @classmethod
    def query_all(cls):
        return cls.query()

    @classmethod
    def query_genre(cls, genre):
        return cls.query(cls.parameters == genre)


class Click(ndb.Model):
    """Models an individual Guestbook entry with content and date."""
    url = ndb.StringProperty(indexed=True)
    # gender = ndb.StringProperty()
    # age = ndb.StringProperty()
    # region = ndb.StringProperty()
    sessionid = ndb.StringProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def query_clicks_since(cls, startdate):

        # TODO filter by start date
        return cls.query()

    @classmethod
    def query_all(cls):
        return cls.query()

    @classmethod
    def query_clicks(cls, url):
        return cls.query(cls.url == url)


    @classmethod
    def get_your_clicks(cls, sessionid):
        return cls.query(cls.sessionid == sessionid)


def getBannerImages(numimages, sessionid, EPSILON):
    youtclicks = Click.get_your_clicks(sessionid).fetch()
    yourcounts = {}
    for item in youtclicks:
        if 'fringetix' in item.url:
            try:
                image = eval(Content.query_content(item.url).fetch()[0].content)['image_uri']
            except:
                continue

            try:
                yourcounts[item.url]['v'] += 1
            except:
                yourcounts[item.url] = {'v':1, 'url': item.url, 'image': image}

    yourcounts = sorted(yourcounts.values(), key= lambda r: r['v'], reverse=True)

    choosecontent = Click.query_all().fetch()
    counts = {}
    for item in choosecontent:
        if 'fringetix' in item.url:
            try:
                image = eval(Content.query_content(item.url).fetch()[0].content)['image_uri']
            except:
                continue

            try:
                counts[item.url]['v'] += 1
            except:
                counts[item.url] = {'v':1, 'url': item.url, 'image': image}

    counts = sorted(counts.values(), key=lambda r: r['v'], reverse=True)

    print counts

    res = []
    for i in range(numimages):
        # expore
        if (random.uniform(0, 1) < EPSILON['v'] or len(yourcounts) == 0) and len(counts) > 0:
            res.append(counts[0]['image'])
            del counts[0]
        # exploit
        elif len(yourcounts) > 0:
            res.append(yourcounts[0]['image'])
            del yourcounts[0]
    return res


# the pk is parameters and url
def checkContainsItem(entity, entitycls, key):
    try:
        if entitycls.query_content(key).fetch():
            return True
    except:
        pass
    return False


def storejsoncontent(jsoncontent, parameters):
    # split up parameters
    parameters = [g.split('=')[-1] for g in parameters.split('&') if g[:len('genre[]=')] == 'genre[]=']

    aggregatelist = set([])
    # TODO not generalised yet
    for item in jsoncontent.get("results", jsoncontent.get('Data', {}).get('Movies', [])):
        key = item.get("url", item.get('MovieUrl'))
        if not checkContainsItem('content', Content, key) and key not in aggregatelist:
            aggregatelist.add(key)
            for param in parameters:
                content = Content(parent=ndb.Key("content", key or "*notitle*"),
                                  content=str(item),
                                  parameters=param,
                                  url=key)
                content.put()

def remixjsoncontent(jsoncontent, parameters, EPSILON):
    print EPSILON
    if EPSILON['v'] == 0:
        return jsoncontent

    parameters = [g.split('=')[-1] for g in parameters.split('&') if g[:len('genre[]=')] == 'genre[]=']
    choosecontent = []
    for param in parameters:
        choosecontent += Content.query_genre(param).fetch()

    if not parameters:
        choosecontent = Content.query_all().fetch()


    if 'results' in jsoncontent.keys():
        # for each results decide to keep or swap out
        totalclicks = 0
        for i in range(len(jsoncontent['results'])):
            # check popularity
            key = jsoncontent['results'][i].get("url",jsoncontent['results'][i].get('MovieUrl'))
            try:
                numclicks = len(list(Click.query_clicks(key).fetch()))
            except:
                numclicks = 0

            jsoncontent['results'][i]['score'] = numclicks
            totalclicks += jsoncontent['results'][i]['score']

        jsoncontent['results'] = sorted(jsoncontent['results'], key=lambda r : r['score'], reverse=True)
        for i in range(len(jsoncontent['results'])):
            # swicth content when
            if random.uniform(0, 1) < (1-(jsoncontent['results'][i]['score']/(totalclicks+1))) * (EPSILON['v']):
                print 'RECOMEND'
                newcontent = eval(choosecontent[randint(0, len(choosecontent)-1)].content)
                # if 'event_type' not in newcontent:
                #     print newcontent
                newcontent['event_type'] = '{} - [BANDITS CHOICE]'\
                    .format(parameters[0] if len(parameters) > 0 else newcontent.get('event_type', ''))
                jsoncontent['results'][i] = newcontent

    return jsoncontent  
    # if any((key in jsoncontent.keys() for key in ['results', 'Data'])):


def fetchclickssince(startdate):
    return Click.query_clicks_since(startdate).fetch()


def addClickTo(url, sessionid):
    key = '/' + '/'.join(url.split('/')[3:])
    # check content exists
    if checkContainsItem('content', Content, key):
        # add click
        print("CLICKED")
        click = Click(parent=ndb.Key("click", key or "*notitle*"),
                      url=key,
                      # gender=GENDER[randint(0, len(GENDER) - 1)],
                      # age=AGES[randint(0, len(AGES) - 1)],
                      # region=REGION[randint(0, len(REGION) - 1)],
                      sessionid=sessionid)
        click.put()