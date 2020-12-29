import requests
import humanize
from cachetools.func import ttl_cache

api_key = '8964acbf6b347c9f18fcb17106398772'

url = "https://financialmodelingprep.com/api/v3/quotes/index?apikey={}".format(api_key)

url_oil = 'https://financialmodelingprep.com/api/v3/quote/CLUSD?apikey={}'.format(api_key)

names = ['NASDAQ Composite', 'S&P 500', 'MOEX Russia Index']
my_names = ['NASDAQ', 'S&P 500', 'MOEX Russia']

_t = humanize.i18n.activate("ru_RU")


def sign(x):
    if float(x) < 0:
        return '-'
    return '+'


def percentage(x):
    if float(x) < 0:
        return str(x) + '%'
    return '+' + str(x) + '%'


def price(x):
    x = round(x, 2)
    return humanize.intcomma(x)


@ttl_cache()
def get_data():
    data = requests.get(url).json()
    out = {}
    for i, name in enumerate(names):
        index = list(filter(lambda x: x['name'] == name, data))[0]
        out[my_names[i]] = [price(index['price']), sign(index['changesPercentage']), percentage(index['changesPercentage'])]

    # нефть
    data = requests.get(url_oil).json()[0]
    out['Нефть'] = [price(data['price']), sign(data['changesPercentage']), percentage(data['changesPercentage'])]
    return out
