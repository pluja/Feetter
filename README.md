<p align="center"><img width="200" src="misc/logo-with-text.png"></p>
<p align="center">Create and manage anonymous feeds in <b>Nitter</b> with a simple and fast web interface.</p>
<p align="center"><a href="https://github.com/pluja">Check out my other privacy projects</a></p>

## Features:
- [x] Create and manage Nitter feeds.
- [x] Save tweets via URL and display them
- [x] Directly visit your Nitter feeds.
- [x] Create as many feeds as you like.
- [x] Lightweight.
- [x] No JS, No Cookies, No tracking.
- [x] No registration: just a randomly generated username.
- [x] Multiplatform, syncs everywhere.

## Install:

### Local run:
1. Clone this repo.
2. Install python3 and python dependencies from `requirements.txt`
3. `mkdir data`
3. Run `sanic feetter.app`
4. Visit http://127.0.0.1:8000

### Run with Docker (Recommended):
> This run uses Gunicorn, so it is instance-ready.
> Docker commands may require to use `sudo`

1. Clone this repo.
  - `git clone https://github.com/pluja/Feetter.git`
3. Install docker.
4. Build the Docker image:
  - `docker build -t feetter .`
5. Run the container:
  - `docker run -p 1337:1337 -d --name feetter feetter`
6. Visit `http://localhost:1337/` and enjoy :)

#### Updating:
- `cd` into the project directory and run `git pull`
- `docker stop`
- Run steps `4` to `6` if you are running Docker.

## Roadmap

- [x] Delete a feed
- [x] Edit a feed: Add users
- [x] Edit a feed: Remove users
- [ ] Edit a feed: Change name
- [ ] Export data as json file
- [ ] Import data from json file
- [ ] Autodelete empty users
- [ ] Display feed tweets in app from rss (less data)

## Screenshots:

### Create new feed:
![Create new feed](https://i.imgur.com/aWziQfG.png)

#### My Feeds page:
![My Feeds](https://i.imgur.com/MrzVpyt.png)


## Built with

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![HTML](https://img.shields.io/badge/HTML-239120?style=for-the-badge&logo=html5&logoColor=white)
![Sanic](https://img.shields.io/badge/-SANIC-ff69b4?style=for-the-badge)
![Jinja2](https://img.shields.io/badge/-Jinja2-B41717?style=for-the-badge&logo=jinja)

> Credit for the logo: https://logodust.com/


## [Support](https://github.com/pluja/pluja/blob/main/SUPPORT.md)
