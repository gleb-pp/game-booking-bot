## Game Booking Bot

### Problem

Innopolis University has a cabinet with board games available to all students. To borrow a game, a student must privately message a staff member to check the game's availability and arrange a meeting. This approach leads to the following inconveniences:
- The employee manually checks the availability of each game, as there is no single source of up-to-date information on game status.
- The employee has to manually record each loaned game.
- The employee has to manually schedule each meeting.
- The student has to wait for the employee's response to each question separately.

### Solution

The developed bot allows students to book games independently:

- **Students** can view the list of available games, select a game and appropriate timeslot.
- **Employee** no longer need to communicate with each student individually; they simply need to mark the available slots in a shared schedule.
- **Non-technical users** can monitor the current status of all games through a Google Sheet, which the bot updates automatically.

## Features

### Authorization
When a user interacts with the bot for the first time, the bot asks the user for their corporate email address, verifies it against the database and reserves it for the user.

<p align="left">
<img src="https://raw.githubusercontent.com/gleb-pp/game-booking-bot/refs/heads/main/pic/auth.jpg" width="250"/>
</p>

### Game Selection
When a user wants to borrow a game, the bot first filters the games by language (to support foreign students) and shows the list of available games.

<p align="left">
<img src="https://raw.githubusercontent.com/gleb-pp/game-booking-bot/refs/heads/main/pic/select.jpg" width="750"/>
</p>

### Meeting Arrangement
The administrator simply needs to mark the available time slots. Afterwards, students can independently sign up for a slot to pick up the game.

<p align="left">
<img src="https://raw.githubusercontent.com/gleb-pp/game-booking-bot/refs/heads/main/pic/timeslot.jpg" width="250"/>
</p>

### Admin panel
The bot offers employee a convenient interface for managing games directly within the chat.

<p align="left">
<img src="https://raw.githubusercontent.com/gleb-pp/game-booking-bot/refs/heads/main/pic/admin.jpg" width="250"/>
</p>

### Google Sheets Integration
The bot records game statuses in a Google Sheets table, allowing non-technical administrators to track game statuses in a browser or application.

<p align="left">
<img src="https://raw.githubusercontent.com/gleb-pp/game-booking-bot/refs/heads/main/pic/sheet.png" width="750"/>
</p>
