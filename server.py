# /path/to/server.py
from sanic import Sanic
from sanic.response import text
from sanic.response import html
from sanic.response import redirect
from sanic.response import html

from jinja2 import Environment, PackageLoader
from bs4 import BeautifulSoup
from simpleicons.all import icons


import httpx
import json
import os, os.path
import re
from random import randrange
import petname

from urllib.parse import unquote

env = Environment(loader=PackageLoader('server','templates'))

app = Sanic("NitterFeeds")

app = Sanic.get_app("NitterFeeds")

FOOTER = f"""<footer class="container">
<pre>by <a href="https://github.com/pluja">Pluja</a>.</pre> <br>
    <b style="font-size:.6em; color:#FB8537;"> <img style="width:2%;" src="https://web.getmonero.org/press-kit/symbols/monero-symbol-480.png"><mark>xmr:</mark> 83czvTQL5cHXZZpRM6bvcqVZSbNRqsX1tMwWnx1HjKBUD8swxUm9fFiTHUZbfYg8qPLM4nLwSdGCM1JmAXUp886KG93Pccr</b><br>
    <b style="font-size:.6em; color:#1372A4;"> <mark>Ł (ltc):</mark> MMSW3AnzHbxnmVeXzGjnNgHf6h62qpR9VA</b></br>
    <b style="font-size:.6em; color:#FEAC48;"> <mark>₿ (btc):</mark> bc1qnrh67j3q0y8kzsxl9npgrlqhalcgx4awa3j2u0</b><br>
</footer>"""

nitterInstances = ["nitter.fdn.fr", "tweet.lambda.dance", "nitter.42l.fr", "nitter.r3d.red", "nitter.eu", "nitter.kavin.rocks"]

sampleFeed = """{
                  "feeds": [
                    {
                      "name": "Example",
                      "users": [
                        "monero",
                        "snowden"
                      ]
                    }
                  ]
                }"""

app.static("/static", "./static")

filename = ""

@app.route("/", name="index")
@app.route("/index", name="index")
async def index(request):
    template = env.get_template('index.html')
    errorHTML = ""
    err = False

    if(request.args):
        args = request.args
        err=args.get("error")

    ls = os.listdir('data')
    usercount = len(ls)

    username = petname.Generate(3, "-", 10)
    # If username exists generate another until its unexistent
    while f'{username}.json' in ls:
        username = petname.Generate(3, "-", 10)

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
    filename = f"data/{username}.json"
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
                    "footer":FOOTER
            }
            return html(template.render(data=data))
        else:
            template = env.get_template('error.html')
            return html(template.render(error="Feed does not exist"))

def validUser(username):
    return (re.match("^[a-z]+?\-+[a-z]+?\-+[a-z]+?\*?$|^\*$", username) and len(username)<31)

@app.get("/delete/<username>/<fromFeed>")
async def delete(request, username=None, fromFeed=None):
    filename = f"data/{username}.json"
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
                    result="deleted"
                    # If no users in feed, delete the feed
                    if len(feed["users"]) == 0:
                        userFeedJson["feeds"].pop(i)
                        result = "feed with 0 users deleted"
                    # Replace JSON file
                    userFeedFile.seek(0)
                    json.dump(userFeedJson, userFeedFile, indent=2)
                    # Deal with smaller data.
                    userFeedFile.truncate()
                    # Return to edit page with success message.
                    url = app.url_for(f"edit", username=username, feedname=fromFeed, result=result)
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
                        json.dump(userFeedJson, userFeedFile, indent=2)
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
    result = None
    if(args):
        username=args.get("username")
        if args.get("result"):
            result=args.get("result")

    filename = f"data/{username}.json"
    try:
        with open(filename, 'r') as userFeedFile:
            pass
    except:
        if validUser(username):
            with open(filename, 'w') as userFeedFile:
                userFeedJson = json.loads(sampleFeed)
                json.dump(userFeedJson, userFeedFile, indent=2)
        else:
            url = app.url_for("index", error="username")
            return redirect(url)


    with open(filename, 'r') as userFeedFile:
        userFeedJson = json.load(userFeedFile)
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
                "feedCards":BeautifulSoup(feedCards),
                "footer":FOOTER
        }
        return html(template.render(data=data))

@app.post("/adduser/<username>/<feed>")
async def newfeed(request, username=None, feed=None):
    body = unquote(request.body.decode())
    regx = r"[^a-zA-Z0-9-\--\._,]"
    newFeedUser = re.sub(regx, '', body.split("=")[1])

    filename = f"data/{username}.json"
    with open(filename, 'r+') as userFeedFile:
        userFeedJson = json.load(userFeedFile)
        for f in userFeedJson["feeds"]:
            if feed == f["name"]:
                if not newFeedUser in f["users"]:
                    f["users"].append(newFeedUser)
                    # Replace JSON file
                    userFeedFile.seek(0)
                    json.dump(userFeedJson, userFeedFile, indent=2)
                    # Deal with smaller data.
                    userFeedFile.truncate()
                    url = app.url_for("edit", username=username, feedname=feed, result=f"{newFeedUser} was added.")
    url = app.url_for("edit", username=username, feedname=feed,result=f"{newFeedUser} not added. Already existing?")
    return redirect(url)

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
        filename = f"data/{username}.json"
        with open(filename, 'r+') as userFeedFile:
            userFeedJson = json.load(userFeedFile)
            userFeedJson["feeds"].append(json.loads(dataJson))

            userFeedFile.seek(0)
            json.dump(userFeedJson, userFeedFile, indent=2)
            url = app.url_for("user", username=username, result=f"{newFeedName} created")
            return redirect(url)
    except:
        url = app.url_for("user", result=0)
        return redirect(url)
    #dataJson = json.dumps(dataJson)
    return text(dataJson)
