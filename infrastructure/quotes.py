import json
from random import randrange


def random_quote():
    with open("data/quotes.json", "r") as data:
        quotes = json.load(data)
        last_key = int(sorted(quotes.keys())[-1])
        rand_key = str(randrange(1,last_key+1))
        rand_quote = quotes.get(rand_key)
        return rand_quote.get('Quote'), rand_quote.get('Author')
