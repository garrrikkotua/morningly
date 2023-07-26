<div id="top"></div>


<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/garrrikkotua/morningly">
    <img src="static/email_website/vector_logo.svg" alt="Logo" width="300">
  </a>

  <h3 align="center">Morningly</h3>

  <p align="center">
    Your open-source newsletter platform. Inspired by Morning Brew
    <br />
    <a href="https://github.com/garrrikkotua/morningly"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/garrrikkotua/morningly">View Demo</a>
    ·
    <a href="https://github.com/garrrikkotua/morningly/issues">Report Bug</a>
    ·
    <a href="https://github.com/garrrikkotua/morningly/issues">Request Feature</a>
  </p>
</div>


<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

This is an open-source platform to launch your own [Morning Brew](https://www.morningbrew.com/) like newsletter. It has all needed features built-in: creating new issues, web portal, role management, delayed sending, subscribe, unsubscribe, automated market info fetching and other cool stuff.

Originally, I used this project internally to host my own russian-speaking version of Morning Brew. I got around 200 users, send more than 10K emails and more than 60% opening rate, so this platform is quite real world tested :)

### Built With

Technology stack is actually pretty simple. It is all powered by Django.


<!-- GETTING STARTED -->
## Getting Started

### Prerequisites
To start using this tool, you probably should need Python or Docker.

### Installation

_Here is the instruction how to start the app using Python:_

1. Clone the repo
   ```sh
   git clone https://github.com/garrrikkotua/morningly.git
   ```
2. Install pip packages
   ```sh
   pip install -r requirements.txt
   ```
3. Initialize the app with a simple SQLite database
   ```sh
   python manage.py migrate
   ```
4. Create a superuser for your app
   ```sh
   python manage.py createsuperuser
   ```
5. Start the app
   ```sh
   python manage.py runserver
   ```
6. Go to the localhost:8000 to test it!

<!-- USAGE EXAMPLES -->
## Usage
To use this app in the production, your probably should get a Mailgun API key. It is the easiest way to send bulk emails.

You can found a template how to configure Mailgun in `email_website/prod_settings.py`.

Docker, Dokku and Heroku deployment tutorials are to be added soon.

<!-- CONTACT -->
## Contact

Igor Kotua - [@garrrikkotua](https://twitter.com/garrrikkotua) - kotuaigor@gmail.com

Project Link: [https://github.com/garrrikkotua/morningly](https://github.com/garrrikkotua/morningly)

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/garrrikkotua/morningly.svg?style=for-the-badge
[contributors-url]: https://github.com/garrrikkotua/morningly/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/garrrikkotua/morningly.svg?style=for-the-badge
[forks-url]: https://github.com/garrrikkotua/morningly/network/members
[stars-shield]: https://img.shields.io/github/stars/garrrikkotua/morningly.svg?style=for-the-badge
[stars-url]: https://github.com/garrrikkotua/morningly/stargazers
[issues-shield]: https://img.shields.io/github/issues/garrrikkotua/morningly.svg?style=for-the-badge
[issues-url]: https://github.com/garrrikkotua/morningly/issues
[license-shield]: https://img.shields.io/github/license/garrrikkotua/morningly.svg?style=for-the-badge
[license-url]: https://github.com/garrrikkotua/morningly/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[product-screenshot]: static/email_website/morningly_landing_image.png

## Other
The project is not really active. But it was fun : )
