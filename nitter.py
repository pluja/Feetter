from bs4 import BeautifulSoup
import httpx
import re


def parse_nitter_tweet(url):
    pattern = re.compile(r"\/status\/[0-9]+")
    content = BeautifulSoup(httpx.get(url).text,features="html.parser")
    if pattern.search(url):
        tweetHtml = content.body.find("div", attrs={'class':'main-tweet'}).find("div", attrs={'class':'timeline-item'})

        divHeader = tweetHtml.find("div", attrs={'class':'tweet-header'})
        divStats = tweetHtml.find("div", attrs={'class':'tweet-stats'})
        divPublished = tweetHtml.find("div", attrs={'class':'tweet-published'})

        username = divHeader.find("div", attrs={'class':'tweet-name-row'}).find("a", attrs={'class':'username'}).text
        date = divHeader.find("div", attrs={'class':'tweet-name-row'}).find("span", attrs={'class':'tweet-date'}).find("a")['title']
        link = divHeader.find("div", attrs={'class':'tweet-name-row'}).find("span", attrs={'class':'tweet-date'}).find("a")['href']
        content = tweetHtml.find("div", attrs={'class':'tweet-content'}).text

        tweet = {
                "id":re.sub(r"[^0-9]+","",link),
                "username":username,
                "date":date,
                "link":link,
                "content":content
        }
        return tweet
    else:
        return False
