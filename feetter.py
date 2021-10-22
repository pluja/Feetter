# /path/to/server.py
from jinja2 import Environment, FileSystemLoader
from datetime import datetime, timedelta
from urllib.parse import unquote

from sanic.response import redirect
from sanic.response import text
from sanic.response import html
from sanic import Sanic

from bs4 import BeautifulSoup
from random import randrange
import os, os.path
import petname
import nitter
import httpx
import json
import re

base_dir = os.path.abspath(os.path.dirname(__name__))
static_dir = os.path.join(base_dir, 'static')
templates_dir = os.path.join(base_dir, 'templates')
data_dir = os.path.join(base_dir, 'data')
env = Environment(loader=FileSystemLoader(templates_dir), autoescape=True)
app = Sanic(__name__)

app.static('/static', static_dir)

FOOTER = f"""<footer class="container">
<pre>by <a href="https://github.com/pluja">Pluja</a>.</pre> <br>
    <b style="font-size:.6em; color:#FB8537;"> <img style="width:2%;" src="https://web.getmonero.org/press-kit/symbols/monero-symbol-480.png"><mark>xmr:</mark> 83czvTQL5cHXZZpRM6bvcqVZSbNRqsX1tMwWnx1HjKBUD8swxUm9fFiTHUZbfYg8qPLM4nLwSdGCM1JmAXUp886KG93Pccr</b><br>
    <b style="font-size:.6em; color:#1372A4;"> <mark>Ł (ltc):</mark> MMSW3AnzHbxnmVeXzGjnNgHf6h62qpR9VA</b></br>
    <b style="font-size:.6em; color:#FEAC48;"> <mark>₿ (btc):</mark> bc1qnrh67j3q0y8kzsxl9npgrlqhalcgx4awa3j2u0</b><br>
</footer>"""

nitterInstances = ["nitter.fdn.fr", "tweet.lambda.dance", "nitter.42l.fr", "nitter.r3d.red", "nitter.eu", "nitter.kavin.rocks"]
sampleFeed = """{"last-seen": "01/01/2009 08:17:59","feeds": [{"name": "Example", "users": ["monero", "snowden"]}], "saved": []}"""

#filename = ""

@app.route("/", name="index")
@app.route("/index", name="index")
async def index(request):
    template = env.get_template('index.html')
    errorHTML = ""
    err = False

    if(request.args):
        args = request.args
        err=args.get("error")

    ls = os.listdir(data_dir)
    usercount = len(ls)

    username = petname.Generate(2, "-", 10)
    # If username exists generate another until its unexistent
    while f'{username}.json' in ls:
        username = petname.Generate(2, "-", 10)

    if err:
        data = {'usercount': usercount,
                'username': username.lower(),
                'error':err
               }
    else:
        data = {'usercount': usercount,
                'username': username.lower(),
                'error':False
               }
    return html(template.render(data=data))

@app.get("/edit", name="edit")
@app.get("/edit/<username>/<feedname>")
async def edit(request, username=None, feedname=None):
    if(request.args):
        args = request.args
        username=args.get("username")
        feedname=args.get("feedname")
        result = args.get("result")
    else:
        result = False

    feedname = unquote(feedname).replace("+", " ")
    filename = f"{data_dir}/{username}.json"
    with open(filename, 'r') as userFeedFile:
        userFeedJson = json.load(userFeedFile)
        ## CHECK IF FEED EXISTS AND GENERATE EDIT TABLE
        exists = False
        tableContent=""
        for feed in userFeedJson["feeds"]:
            if feed["name"] != feedname:
                continue
            else:
                exists = True
                i = 1
                for user in feed["users"]:
                    instance = nitterInstances[randrange(0, len(nitterInstances))]
                    tableContent+=f"""
                                    <tr>
                                    <th scope="row">{i}</th>
                                    <td><a href="https://{instance}/{user}" target="_blank">@{user}</a></td>
                                    <td><a href="/delete/{username}/{feedname}?deleteUser={user}">❌</a></td>
                                    </tr>
                                  """
                    i+=1
        if exists:
            ## RETURN FEED EDIT PAGE
            template = env.get_template('edit.html')
            data = {
                    "username":username,
                    "feedname":feedname,
                    "table":tableContent,
                    "i":i-1,
                    "result":result,
                    "footer":BeautifulSoup(FOOTER)
            }
            return html(template.render(data=data))
        else:
            template = env.get_template('error.html')
            return html(template.render(error="Feed does not exist", ret=f"/edit/{username}"))

def validUser(username):
    return (re.match("^[a-z]+?\-+[a-z]+?\*?$|^\*$", username) and len(username)<31)

@app.get("/delete/<username>/<fromFeed>")
async def delete(request, username=None, fromFeed=None):
    filename = f"{data_dir}/{username}.json"
    toDelete = None
    args = request.args
    if(args):
        toDelete=args.get("deleteUser")
        userAction=args.get("userAction")
    try:
        with open(filename, 'r') as userFeedFile:
            pass
    except:
        url = app.url_for("index", error="username")
        return redirect(url)

    if toDelete: # We want to dete a user
        with open(filename, 'r+') as userFeedFile:
            i = 0
            userFeedJson = json.load(userFeedFile)
            for feed in userFeedJson["feeds"]:
                if feed["name"] == fromFeed and toDelete in feed["users"]:
                    # Delete user from feed.
                    feed["users"].pop(feed["users"].index(toDelete))
                    # Set the result status
                    # If no users in feed, delete the feed
                    if len(feed["users"]) == 0:
                        userFeedJson["feeds"].pop(i)
                        userFeedFile.seek(0)
                        json.dump(userFeedJson, userFeedFile)
                        userFeedFile.truncate()
                        result = "feed with 0 users deleted"
                        url = app.url_for(f"user", username=username, result=result)
                        return redirect(url)
                    # Overwrite Json file
                    userFeedFile.seek(0)
                    json.dump(userFeedJson, userFeedFile)
                    userFeedFile.truncate()
                    result="deleted"
                    url = app.url_for("edit", username=username, feedname=fromFeed, result=result)
                    return redirect(url)
                ++i
    else: #Whole feed
        if userAction == "True":
            with open(filename, 'r+') as userFeedFile:
                userFeedJson = json.load(userFeedFile)
                for feed in userFeedJson["feeds"]:
                    if feed["name"] == fromFeed:
                        userFeedJson["feeds"].remove(feed)
                        # Replace JSON file
                        userFeedFile.seek(0)
                        json.dump(userFeedJson, userFeedFile)
                        # Deal with smaller data.
                        userFeedFile.truncate()
                        url = app.url_for(f"user", username=username, result=f"delete {fromFeed} feed OK.")
                        return redirect(url)
    return text("Oops! Something went wrong! Error in /delete")

# http://127.0.0.1:8000/user/1234?key1=val1&key2=val2&key3=val3
@app.get("/user")
@app.get("/user/<username>", name="user")
async def user(request, username=None):
    template = env.get_template('user.html')
    args = request.args
    result = False
    if(args):
        username=args.get("username")
        result=args.get("result")

    filename = f"{data_dir}/{username}.json"
    try:
        with open(filename, 'r') as userFeedFile:
            pass
    except:
        if validUser(username):
            with open(filename, 'w') as userFeedFile:
                userFeedJson = json.loads(sampleFeed)
                json.dump(userFeedJson, userFeedFile)
        else:
            url = app.url_for("index", error="username")
            return redirect(url)

    with open(filename, 'r+') as userFeedFile:
        userFeedJson = json.load(userFeedFile)
        lastseen = datetime.strptime(userFeedJson["last-seen"],"%d/%m/%Y %H:%M:%S")
        lastseen += timedelta(minutes=30)
        if lastseen < datetime.now():
            userFeedJson["last-seen"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            userFeedFile.seek(0)
            json.dump(userFeedJson, userFeedFile)
            userFeedFile.truncate()

        feedCards = ""
        for feed in userFeedJson["feeds"]:
            count = 0
            snippet = ""
            instance = nitterInstances[randrange(0, len(nitterInstances))]
            baseUrl = f"https://{instance}/"
            for user in feed["users"]:
                if count < len(feed["users"])-1:
                    if count < 3:
                        snippet += user+", "
                    baseUrl += user+','
                else:
                    snippet += user+"..."
                    baseUrl += user
                count+=1
            feedCards += f"""
                        <a href='{baseUrl}' target='_blank'><article>
                          <h3>{feed["name"]} Feed</h3>
                          <p>{snippet}</p>
                          <a href='{baseUrl}' role='button' class='outline' target="_blank">Open Feed</a>
                          <a href='/edit/{username}/{feed["name"]}' role='button' class='contrast outline'>Edit Feed</a>
                          <a href='/delete/{username}/{feed["name"]}?userAction=True' role='button' class='secondary outline'>Delete Feed</a>
                        </article></a>
                        """
        data = {
                "username":username,
                "result":result,
                "feedCards":BeautifulSoup(feedCards, features="html5lib"),
                "footer":BeautifulSoup(FOOTER)
        }
        return html(template.render(data=data))

@app.post("/adduser/<username>/<feed>")
async def newfeed(request, username=None, feed=None):
    body = unquote(request.body.decode())
    regx = r"[^a-zA-Z0-9-\--\._,]"
    newFeedUser = re.sub(regx, '', body.split("=")[1])

    filename = f"{data_dir}/{username}.json"
    with open(filename, 'r+') as userFeedFile:
        userFeedJson = json.load(userFeedFile)
        for f in userFeedJson["feeds"]:
            if feed == f["name"]:
                if not newFeedUser in f["users"]:
                    f["users"].append(newFeedUser)
                    # Replace JSON file
                    userFeedFile.seek(0)
                    json.dump(userFeedJson, userFeedFile)
                    # Deal with smaller data.
                    userFeedFile.truncate()
                    url = app.url_for("edit", username=username, feedname=feed, result=f"{newFeedUser} added.")
                    return redirect(url)
    url = app.url_for("edit", username=username, feedname=feed,result=f"{newFeedUser} not added. Already existing?")
    return redirect(url)



@app.post("/savetweet/<username>")
async def saveTweet(request, username=None):
    body = unquote(request.body.decode())
    regx = r"[^a-zA-Z0-9-\--\._/:]"
    url = re.sub(regx, '', body.split("=")[1][:-1])
    tweet = nitter.parse_nitter_tweet(url)

    filename = f"{data_dir}/{username}.json"
    with open(filename, 'r+') as userFeedFile:
        userFeedJson = json.load(userFeedFile)
        userFeedJson["saved"].append(tweet)
        userFeedFile.seek(0)
        json.dump(userFeedJson, userFeedFile)
        # Deal with smaller data.
        userFeedFile.truncate()
        url = app.url_for("saved", username=username, result=f"Tweet saved.")
    return redirect(url)

@app.get("/deletesaved/<username>")
async def saved(request, username=None):
    tweetId=request.args.get("id")
    filename = f"{data_dir}/{username}.json"
    with open(filename, 'r+') as userFeedFile:
        userFeedJson = json.load(userFeedFile)
        for saved in userFeedJson["saved"]:
            if saved['id'] == tweetId:
                userFeedJson["saved"].remove(saved)
                userFeedFile.seek(0)
                json.dump(userFeedJson, userFeedFile)
                # Deal with smaller data.
                userFeedFile.truncate()
                url = app.url_for("saved", username=username, result=f"Tweet deleted.")
            else:
                url = app.url_for("saved", username=username, result=f"Error unknown.")
        return redirect(url)


@app.route("/saved/<username>")
async def saved(request, username=None):
    if request.args.get("result"):
        result=request.args.get("result")
    else:
        result = False
    filename = f"{data_dir}/{username}.json"
    template = env.get_template('saved.html')
    tableContent = ""
    with open(filename, 'r+') as userFeedFile:
        userFeedJson = json.load(userFeedFile)
        divU = '<div style="padding:1em;" class="grid">'
        divL = '</div>'
        for saved in userFeedJson["saved"]:
            ind = userFeedJson["saved"].index(saved)
            tableContent += f"""
                            <tr>
                                <th scope="row">{ind+1}</th>
                                <td>{saved['username']}</td>
                                <td>{saved['content']}</td>
                                <td><a href=https://{nitterInstances[randrange(0, len(nitterInstances))]}{saved['link']} target="_blank"> Nitter </a></td>
                                <td><a href="/deletesaved/{username}?id={saved['id']}">🗑️</a></td>
                            </tr>
                            """
        data = {"username":username,
                "tableContent":tableContent,
                "result":result
                }
    return html(template.render(data=data))

@app.post("/newfeed/<username>")
async def newfeed(request, username=None, newFeedName=None, usernames=None):
    args = request.args
    if(args):
        username=args.get("username")
        newFeedName=args.get("feedname")
        newFeedUsers=args.get("usernames").split(",")

    body = unquote(request.body.decode()).split("&")
    regx = r"[^a-zA-Z0-9-\--\._,]"
    newFeedUsers = re.sub(regx, '', body[0].split("=")[1]).split(",")

    regx = r"[^a-zA-Z0-9-\--\._,\s]"
    newFeedName = re.sub(regx, '', body[1].split("=")[1])

    dataJson = {
                  "name":newFeedName,
                  "users":[]
                }

    dataJson["users"]+=newFeedUsers

    dataJson = json.dumps(dataJson)

    try:
        filename = f"{data_dir}/{username}.json"
        with open(filename, 'r+') as userFeedFile:
            userFeedJson = json.load(userFeedFile)
            userFeedJson["feeds"].append(json.loads(dataJson))

            userFeedFile.seek(0)
            json.dump(userFeedJson, userFeedFile)
            url = app.url_for("user", username=username, result=f"{newFeedName} created")
            return redirect(url)
    except:
        url = app.url_for("user", result=0)
        return redirect(url)
    #dataJson = json.dumps(dataJson)
    return text(dataJson)
