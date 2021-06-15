# /path/to/server.py
from sanic import Sanic
from sanic.response import text
from sanic.response import html
from sanic.response import redirect

import httpx
import json
import os, os.path
import re
from random import randrange
import petname

from urllib.parse import unquote

app = Sanic("NitterFeeds")

app.config.DB_NAME = 'NitterFeeds'
app.config['DB_USER'] = 'nitterfeeds'

db_settings = {
    'DB_HOST': 'localhost',
    'DB_NAME': 'NitterFeeds',
    'DB_USER': 'nitterfeeds'
}
app.config.update(db_settings)

app = Sanic.get_app("NitterFeeds")

FOOTER = """<footer class="container">
<mark>by <a href="https://github.com/pluja">Pluja</a>.</mark> <br>
<kbd>xmr: of02ij30jf0ajs0idjf0jq0fj0ejf0j0dwfji0ajdifjsafijsodfjoasj0fjasdfjasjdf0jqifj0J</kbd><br>
<kbd>btc: bc1920jf0aisjdfdwklfjalskjflas</kbd><br>
<kbd>eth: 0x1d9f9jf939jf9as9</kbd>
</footer>"""

nitterInstances = ["nitter.fdn.fr", "tweet.lambda.dance", "nitter.kavin.rocks", "nitter.42l.fr"]

sampleFeed = """{
                  "feeds": [
                    {
                      "name": "Example Feed",
                      "users": [
                        "monero",
                        "snowden",
                        "bitcoin"
                      ]
                    }
                  ]
                }"""

'''
@app.on_request
async def run_before_handler(request):
    request.ctx.user = await fetch_user_by_token(request.token)

@app.route('/hi')
async def hi_my_name_is(request):
    return text("Hi, my name is {}".format(request.ctx.user.name))
'''

app.static("/static", "./static")

filename = ""

@app.on_request
async def setup_before_request(request):
    pass

@app.route("/", name="index")
@app.route("/index", name="index")
async def handler(request):
    #random_username = random_username.generate.generate_username()
    errorHTML = ""
    args = request.args
    if(args):
        err=args.get("error")
        errorHTML = f"<h6 color='red' style='color:red;'> > Error: {err} not valid"


    ls = os.listdir('data')
    usercount = len(ls)

    username = petname.Generate(3, "-")

    while f'{username}.json' in ls:
        username = petname.Generate(3, "-")

    return html(f"""
                    <html lang="en" data-theme="dark">
                      <head>
                        <meta charset="utf-8">
                        <link rel="stylesheet" href="/static/css/pico.min.css">
                        <title>My Feeds</title>
                      </head>
                      <body>
                        <header class="container">
                            {errorHTML}
                            <h4> We have {usercount} users! </h4>
                            <p>
                                <u>Pick this new username:</u> <kbd>{username.lower()}</kbd>
                                <br>
                                <small>Copy and save this username to recover your data</small>
                            </p>

                            <form action="/user" method="get">
                              <label for="email">Enter a valid username</label>
                              <input type="text" id="username" name="username" value={username.lower()} required>
                              <small>A username is not active until it has at least one feed.</small>

                              <!-- Button -->
                              <button class="outline" type="submit">Start feeding</button>
                            </form>
                        </header>
                      </body
                     </html>
                """) #Main page HTML

@app.get("/edit")
@app.get("/edit/<username>/<feedname>")
async def edit(request, username=None, feedname=None):
    args = request.args
    if(args):
        username=args.get("username")
        feedname=args.get("feedname")

    filename = f"data/{username}.json"
    with open(filename, 'r') as userFeedFile:
        userFeedJson = json.load(userFeedFile)
        tableHead = """
                    <table>
                      <thead>
                        <tr>
                          <th scope="col">#</th>
                          <th scope="col">Username</th>
                          <th scope="col">Action</th>
                        </tr>
                      </thead>
                      <tbody>
                    """

        tableClosing = """</tbody>
                        </table>
                       """

        tableContent=""

        ## GENERATE EDIT TABLE
        exists = False
        for feed in userFeedJson["feeds"]:
            if feed["name"] != feedname:
                continue
            else:
                exists = True
                i = 1
                for user in feed["users"]:
                    tableContent+=f"""
                                    <tr>
                                    <th scope="row">{i}</th>
                                    <td>@{user}</td>
                                    <td><a href="">❌</a></td>
                                    </tr>
                                  """
                    i+=1

        ## CREATE TABLE HTML
        table = tableHead+tableContent+tableClosing

        if exists:
            ## RETURN FEED EDIT PAGE
            return html(f"""
                            <html lang="en" data-theme="dark">
                              <head>
                                <meta charset="utf-8">
                                <link rel="stylesheet" href="/static/css/pico.min.css">
                                <title>My Feeds</title>
                              </head>
                              <body>
                                <main class="container">
                                    <h2> Editing <a href="/user/{username}"><kbd>{username}</kbd></a> <b>{feedname}</b> feed</h2>
                                    {table}
                                </main>
                                {FOOTER}
                              </body
                             </html>
                        """)
        else:
            # RETURN ERROR
            return html(f"""
                            <html lang="en" data-theme="dark">
                              <head>
                                <meta charset="utf-8">
                                <link rel="stylesheet" href="/static/css/pico.min.css">
                                <title>My Feeds</title>
                              </head>
                              <body>
                                <main class="container">
                                    <h2> Hey <a href="/user/{username}"><kbd>{username}</kbd></a> <b>{feedname}</b> is not in your feeds</h2>
                                </main>
                              </body
                             </html>
                        """)

def validUser(username):
    return (re.match("^[a-z]+?\-+[a-z]+?\-+[a-z]+?\*?$|^\*$", username))

# http://127.0.0.1:8000/user/1234?key1=val1&key2=val2&key3=val3
@app.get("/user")
@app.get("/user/<username>", name="user")
async def user(request, username=None):
    '''
    async with httpx.AsyncClient() as client:
        r = await client.get('https://fsf.org/')
        print(r.status_code)
        headers = r.headers
    '''
    args = request.args
    result = None
    if(args):
        username=args.get("username")
        if args.get("result"):
            result=args.get("result")

        '''
        print(request.args)
        print(args.get("username"))
        print(request.args.getlist("key1"))
        print(request.query_args)
        print(request.query_string)
        '''

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
                          <a href='#' role='button' class='secondary outline'>Delete Feed</a>
                        </article></a>

                        """

        newFeedCreatorHtml = f"""<details>
                        <summary>Create new feed</summary>
                        <div class="grid">
                          <form action="/newfeed/{username}" method="post" id="json">
                            <label for="usernames">
                              Usernames
                              <input type="text" id="usernames" name="usernames" placeholder="@monero, @signalapp" required>
                            </label>

                            <label for="feedname">
                              Feed Name
                              <input type="text" id="feedname" name="feedname" placeholder="Privacy Feed" required>
                            </label>
                          </div>
                          <button type="submit" class="contrast">Create</button>
                        </form>
                      </details>
                  """

        if result == 1:
            resultHTML = f"<h6 color='green' style='color:green;'> > Feed has been added."
        else:
            if result == 0:
                errorHTML = f"<h6 color='red' style='color:red;'> > Error adding feed."

        return html(f"""
                        <html lang="en" data-theme="dark">
                          <head>
                            <meta charset="utf-8">
                            <link rel="stylesheet" href="/static/css/pico.min.css">
                            <title>My Feeds</title>
                          </head>
                          <body>
                            <main class="container">
                                <hgroup>
                                <h2> <a href="/user/{username}"><kbd>{username}</kbd></a> Feeds</h2>
                                <h6 style="font-size: .7em;">*Save your profile with <a href="/user/{username}">this link</a></h6>
                                </hgroup>

                                {newFeedCreatorHtml}
                                {feedCards}
                            </main>
                            {FOOTER}
                          </body
                         </html>
                    """)

@app.post("/newfeed/<username>")
async def newfeed(request, username=None, newFeedName=None, usernames=None):
    args = request.args
    if(args):
        username=args.get("username")
        newFeedName=args.get("feedname")
        newFeedUsers=args.get("usernames").replace("@", "").replace(" ","").split(",")

    body = unquote(request.body.decode()).split("&")
    regx = r"[^a-zA-Z0-9-\--\._, ]"
    newFeedUsers = re.sub(regx, '', body[0].split("=")[1]).split(",")
    newFeedName = body[1].split("=")[1]

    dataJson = {
                  "name":newFeedName.replace("+", " "),
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
            url = app.url_for("user", username=username, result=1)
            return redirect(url)
    except:
        url = app.url_for("user", result=0)
        return redirect(url)
    #dataJson = json.dumps(dataJson)
    return text(dataJson)

@app.route("/cookie")
async def test(request):
    response = text("There's a cookie up in this response")
    response.cookies["test"] = "It worked!"
    response.cookies["test"]["domain"] = ".yummy-yummy-cookie.com"
    response.cookies["test"]["httponly"] = True
    return response
