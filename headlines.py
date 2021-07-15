import feedparser
from flask import Flask , render_template, request
import json
import urllib
import urllib.request as urllib2
import urllib.parse


app = Flask(__name__)


RSS_FEEDS = {'bbc' : 'http://feeds.bbci.co.uk/news/rss.xml',
            'cnn': 'http://rss.cnn.com/rss/edition.rss',
            'fox': 'http://feeds.foxnews.com/foxnews/latest',
            'iot': 'http://www.iol.co.za/cmlink/1.640'}
DEFAULTS = {'publication': 'bbc',
            'city':'Kyiv,UA',
            'currency_from':'GBP',
            'currency_to':'USD'}
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=caa98b823acf3265886a5176992ed963"

CURRENCY_URL = "https://openexchangerates.org/api/latest.json?app_id=99bcd45fd3304f97b2cb11df10f3c138"
@app.route("/")
def home():
    publication = request.args.get('publication')
    if not publication:
        publication = DEFAULTS['publication']
    articles = get_news(publication)
    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)
    currency_from = request.args.get('currency_from')
    if not currency_from:
        currency_from = DEFAULTS['currency_from']
    currency_to = request.args.get('currency_to')
    if not currency_to:
        currency_to = DEFAULTS['currency_to']
    rate, currencies = get_rate(currency_from,currency_to)
    return render_template("home.html", articles=articles,
                           weather=weather,
                           currency_to=currency_to,
                           currency_from=currency_from,
                           rate=rate,
                           currencies=sorted(currencies))


def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS['publication']
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']

def get_weather(query):
        query = urllib.parse.quote(query)
        url = WEATHER_URL.format(query)
        data = urllib.request.urlopen(url)
        parsed = json.load(data)
        weather = None
        if parsed.get("weather"):
            weather = {"description": parsed["weather"][0]["description"],
                       "temperature":parsed["main"]["temp"],
                       "city":parsed["name"],
                       'country':parsed['sys']['country']}
        return weather

def get_rate(frm,to):
    all_currency = urllib.request.urlopen(CURRENCY_URL)

    parsed = json.load(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (to_rate/frm_rate,parsed.keys())



if __name__ == '__main__':
    app.run(port=5000, debug=True)
