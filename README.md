# Space Run - Race for Family

A thrilling 2D space racing game where you must win a deadly race to save your family from a crime lord's clutches!

## Credits
- **Created by**: Kaii
- **GitHub**: [kaii](https://github.com/prakit1234)
-**Avatar**: ![Kaii's Avatar](https://camo.githubusercontent.com/41e66d161f44695150f4f312969b95e229083dec78d6a0d652a7d41160790807/68747470733a2f2f692e6962622e636f2f74504c32544b44592f746f6a692e706e67)
- **Co_partner**:[Pd](https://github.com/PDgaming)


## Story
You were once a famous space racer, living a peaceful life with your family. When a wealthy crime lord, Mr. X, approached you to throw the race for his gambling ring, you refused. Now he's taken your family hostage! You must win this deadly race to save them, but beware - other racers will cheat and sabotage you!

## Requirements
- Python 3.x
- Pygame

## Installation
1. Make sure you have Python installed on your system
2. Install the required dependencies:
```
pip install -r requirements.txt
```

## How to Play
1. Run the game:
```
python main.py
```

2. Main Menu:
   - Use UP/DOWN arrows to navigate
   - Press N to edit your player name
   - Press I to edit host IP when joining
   - Press ENTER to select options

3. Typing Controls:
   - Press N to start typing your name
   - Press I to start typing the host's IP address
   - Use BACKSPACE to delete characters
   - Press ENTER when done typing
   - Name rules:
     - Up to 12 characters
     - Only letters and numbers allowed
   - IP address rules:
     - Only numbers and dots allowed
     - Format: XXX.XXX.XXX.XXX

4. Finding Your IP Address:
   - Make sure both players are on the same network (same WiFi)
   - Use your local network IP (usually starts with 192.168.x.x)
   - Don't use your public IP address

   Windows:
   1. Open Command Prompt (Windows + R, type "cmd")
   2. Type `ipconfig` and press Enter
   3. Look for "IPv4 Address" under your network adapter

   Mac:
   1. Open System Preferences
   2. Click on Network
   3. Select your active network connection
   4. Your IP address will be shown

   Linux:
   1. Open Terminal
   2. Type `ifconfig` or `ip addr`
   3. Look for your network interface
   4. Find the "inet" address

5. Multiplayer Setup:
   - One player should select "Host Game"
   - The other player should select "Join Game" and enter the host's IP address
   - Both players must be on the same network
   - Port 5000 must be open for TCP connections

6. Game Controls:
   - LEFT and RIGHT arrow keys: Move your spaceship
   - P key: Activate power-up
   - ESC key: Pause game
   - SPACE key: 
     - Advance through the story
     - Restart the game after game over

7. Pause Menu:
   - ESC to pause/unpause
   - UP/DOWN to navigate options
   - ENTER to select:
     - Resume: Continue the game
     - Restart: Start a new game
     - Exit to Menu: Return to main menu

## Game Features
- Network multiplayer support
- Customizable player names
- Pause menu with multiple options
- Story-driven gameplay with multiple scenes
- Two types of obstacles:
  - Red obstacles: Regular obstacles that fall straight down
  - Yellow obstacles: Cheating racers that move unpredictably
- Lives system (3 lives)
- Score system (points for dodging obstacles)
- Game over screen with restart option
- Power-ups:
  - Speed Boost: Temporarily increases your speed
  - Shield: Makes you invincible for a short time
  - Time Slow: Slows down obstacles temporarily
- Enhanced enemies with special abilities:
  - Teleporting enemies
  - Homing missiles
  - Energy shields

## Tips
- Watch out for yellow obstacles - they move unpredictably!
- Try to maintain a high score by dodging as many obstacles as possible
- You have 3 lives - use them wisely!
- Collect power-ups to gain an advantage
- Be careful of enhanced enemies - they're more dangerous than regular ones!
- Coordinate with your friend to avoid collisions
- Use the pause menu to take breaks or restart if needed
- Make sure both players are on the same network before starting
- If connection fails, check your firewall settings for port 5000

## Game Over
When you lose all your lives, the game ends. Press SPACE to restart and try again!

## Network Requirements
- Both players must be on the same local network
- Port 5000 must be open for TCP connections
- The host must know their IP address to share with other players
- If having connection issues:
  1. Check if both players are on the same network
  2. Verify the IP address is correct
  3. Ensure port 5000 is not blocked by firewall
  4. Try disabling antivirus temporarily
  5. Check if your router allows local network connections 