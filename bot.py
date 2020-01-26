import random
import time


from lxml.html import fromstring
import nltk
nltk.download('punkt')
import requests

from twitter import OAuth, Twitter


import credentials

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

oauth = OAuth(
        credentials.ACCESS_TOKEN,
        credentials.ACCESS_SECRET,
        credentials.CONSUMER_KEY,
        credentials.CONSUMER_SECRET
    )
t = Twitter(auth=oauth)

HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
                      ' AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'
        }


def extract_paratext(paras):
    paras = [para.text_content() for para in paras if para.text_content()]
    para = random.choice(paras)
    return tokenizer.tokenize(para)


def extract_text(para):
    for _ in range(10):
        text = random.choice(para)
        if text and 60 < len(text) < 210:
            return text

    return None


def scrape_guardian():
    url = 'https://www.theguardian.com/uk/technology'
    r = requests.get(url, headers=HEADERS)
    tree = fromstring(r.content)
    links = tree.xpath('//div[@class="fc-item__container"]/a/@href')

    for link in links:
        r = requests.get(link, headers=HEADERS)
        blog_tree = fromstring(r.content)
        paras = blog_tree.xpath('//div[@class="content__article-body from-content-api js-article__body"]/p')
        para = extract_paratext(paras)
        text = extract_text(para)
        if not text:
            continue

        yield '"%s" %s' % (text, link)


def main():
    print('Bot started.')
    news_funcs = ['scrape_guardian']
    news_iterators = []
    for func in news_funcs:
        news_iterators.append(globals()[func]())
    while True:
        for i, iterator in enumerate(news_iterators):
            try:
                tweet = next(iterator)
                t.statuses.update(status=tweet)
                print(tweet, end='\n')
                time.sleep(600)
            except StopIteration:
                news_iterators[i] = globals()[newsfuncs[i]]()


if __name__ == "__main__":
    main()