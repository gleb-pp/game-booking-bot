# Game Booking Bot

The bot helps students and staff at Innopolis University to book board games and choose a meeting time. 

## Project Context

### Problem

Innopolis University has a cabinet with board games available to all students. To borrow a game, students need to send a private message to a staff member, check the availability of the game, and arrange a meeting. Such approach leads to the following inconveniences:
- The employee manually checks the availability of each game separately; there is no single source of up-to-date status for each game.
- The employee has to manually record each game issued.
- The employee has to manually schedule each meeting.
- The student has to wait for the employee's response to each question separately.

### Solution

Solution

## Features

### Authorization
When user interacts with the bot for the first time, the bot asks user for their corporate email address, verifies in the database and reserves for the user.

<p align="center">
<img src="https://raw.githubusercontent.com/gleb-pp/game-booking-bot/refs/heads/main/pic/auth.jpg" width="200"/>
</p>

### Game Selection
When user want to take a game, the bot filters the games by language and shows the list of available games.

<p align="center">
<img src="https://raw.githubusercontent.com/gleb-pp/game-booking-bot/refs/heads/main/pic/select.jpg" width="200"/>
</p>

### Timeslot 
When user selected the game to take, the bot suggests to choose an appropriate timeslot.

<p align="center">
<img src="https://raw.githubusercontent.com/gleb-pp/game-booking-bot/refs/heads/main/pic/timeslot.jpg" width="200"/>
</p>

### Admin panel
The bot 

### Google Sheets Integration


### Built With

[![FastAPI][FastAPI]][FastAPI-url]
[![React][React]][React-url]
[![PostgreSQL][PostgreSQL]][PostgreSQL-url]
[![NginX][NginX]][NginX-url]
[![Docker][Docker]][Docker-url]

[FastAPI]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi
[FastAPI-url]: https://fastapi.tiangolo.com/