<p align="center"><img width="200" src="misc/logo-with-text.png"></p>
<p align="center">Create and manage anonymous feeds in <b>Nitter</b> with a simple and fast web interface.</p>
<p align="center"><a href="https://github.com/pluja">Check out my other privacy projects</a></p>

- [Features](#features)
- [Install](#install)
  - [Local run](#local-run)
  - [Run with Docker](#run-with-docker)
- [Roadmap](#roadmap)
- [Screenshots](#screenshots)
- [Built with](#built-with)
- [Public Instances](#public-instances)

## Features
- [x] Create and manage Nitter feeds.
- [x] Save tweets via URL and display them
- [x] Directly visit your Nitter feeds.
- [x] Create as many feeds as you like.
- [x] Lightweight.
- [x] No JS, No Cookies, No tracking.
- [x] No registration: just a randomly generated username.
- [x] Multiplatform, syncs everywhere.

## Install

### Local run
1. Clone this repo.
2. Install python3 and python dependencies from `requirements.txt`
3. `mkdir data`
3. Run `sanic feetter.app`
4. Visit http://127.0.0.1:8000

### Run with Docker
> This run uses Gunicorn, so it is instance-ready.
> Docker commands may require to use `sudo`

1. Install docker.
2. Pull the image: `docker pull pluja/feetter`
3. Run the container:
  - `docker run -p 1337:1337 -d --name feetter pluja/feetter`
4. Visit `http://localhost:1337/` and enjoy :)

#### Updating
- Run `docker pull pluja/feetter`
- Run `docker stop feetter`
- Run `docker rm feetter`
- Run `docker run -p 1337:1337 -d --name feetter pluja/feetter`

## Roadmap

- [x] Delete a feed
- [x] Edit a feed: Add users
- [x] Edit a feed: Remove users
- [ ] Optimize for small screens.
- [ ] Edit a feed: Change name
- [ ] Export data as json file
- [ ] Import data from json file
- [ ] Autodelete empty users
- [ ] Display feed tweets in app from rss (less data)

## Screenshots

### Create new feed
![Create new feed](https://i.imgur.com/aWziQfG.png)

#### My Feeds page
![My Feeds](https://i.imgur.com/MrzVpyt.png)


## Built with

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![HTML](https://img.shields.io/badge/HTML-239120?style=for-the-badge&logo=html5&logoColor=white)
![Sanic](https://img.shields.io/badge/-SANIC-ff69b4?style=for-the-badge)
![Jinja2](https://img.shields.io/badge/-Jinja2-B41717?style=for-the-badge&logo=jinja)

> Credit for the logo: https://logodust.com/


## [Support](https://github.com/pluja/pluja/blob/main/SUPPORT.md)
### Public Instances
| Instance	| Server	|
|-	|-	|
| [feetter.r3d.red](feetter.r3d.red) 	| 🇩🇪 	|
