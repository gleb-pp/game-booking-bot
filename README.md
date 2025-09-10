## Game Booking Bot

### Problem

Innopolis University has a cabinet with board games available to all students. To borrow a game, students need to send a private message to a staff member, check the availability of the game, and arrange a meeting. Such approach leads to the following inconveniences:
- The employee manually checks the availability of each game separately; there is no single source of up-to-date status for each game.
- The employee has to manually record each game issued.
- The employee has to manually schedule each meeting.
- The student has to wait for the employee's response to each question separately.

### Solution

The developed bot allows students to book games on their own:

- **Students** can view the list of available games, select a game and appropriate timeslot.
- **Employees** do not need to communicate with each student individually; they only need to indicate the available slots in the table.
- **Non-technical users** can monitor the current list of games in Google Sheets table, where the bot indicates the statuses.

## Features

### Authorization
When user interacts with the bot for the first time, the bot asks user for their corporate email address, verifies in the database and reserves for the user.

<p align="left">
<img src="https://raw.githubusercontent.com/gleb-pp/game-booking-bot/refs/heads/main/pic/auth.jpg" width="250"/>
</p>

### Game Selection
When user want to take a game, the bot filters the games by language (to support foreign students) and shows the list of available games.

<p align="left">
<img src="https://raw.githubusercontent.com/gleb-pp/game-booking-bot/refs/heads/main/pic/select.jpg" width="750"/>
</p>

### Meeting Arrangement
The administrator simply needs to mark the available time slots, after which students can sign up for the game giveaway themselves.

<p align="left">
<img src="https://raw.githubusercontent.com/gleb-pp/game-booking-bot/refs/heads/main/pic/timeslot.jpg" width="250"/>
</p>

### Admin panel
The bot offers employees a convenient interface for manipulating games directly in the chat.

<p align="left">
<img src="https://raw.githubusercontent.com/gleb-pp/game-booking-bot/refs/heads/main/pic/admin.jpg" width="250"/>
</p>

### Google Sheets Integration
The bot records game statuses in a Google Sheets table, allowing non-technical administrators to track game statuses in a browser or application.

<p align="left">
<img src="https://raw.githubusercontent.com/gleb-pp/game-booking-bot/refs/heads/main/pic/sheet.jpg" width="750"/>
</p>