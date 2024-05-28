# HAMSTER KOMBAT Manager

HAMSTER KOMBAT Manager is a Python application that automates interaction with
the [Hamster Kombat](https://t.me/hamster_kombat_bot) game through Telegram. This bot allows you to manage sessions,
perform daily tasks, upgrade your profile, and send taps to the game.

## Features

- Create, list, and delete sessions
- Automate daily tasks and upgrades
- Configure tapping settings
- Retry mechanism for robustness
- Upcoming features:
    - Proxy support
    - Automatic execution of certain tasks
    - Minor bug fixes
    - Additional features

## Requirements

- Python 3.12
- Docker (for containerized deployment)
- A Telegram account and API credentials

## Installation

### Using Docker

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/hamster-bot-manager.git
    cd hamster-bot-manager
    ```

2. **Create a `.env` file**:
    ```sh
    cp .env.example .env
    ```
   Fill in your API credentials and other configuration settings in the `.env` file.

3. **Build the Docker image**:
    ```sh
    docker build -t hamster-bot-manager .
    ```

4. **Run the Docker container**:
    ```sh
    docker run --env-file .env -v $(pwd)/sessions:/app/sessions hamster-bot-manager
    ```

### Using Docker Compose

Instead of building and running your own Docker container, you can use `docker-compose.yml` for a simplified setup.

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/hamster-bot-manager.git
    cd hamster-bot-manager
    ```

2. **Create a `.env` file**:
    ```sh
    cp .env.example .env
    ```
   Fill in your API credentials and other configuration settings in the `.env` file.

3. **Run Docker Compose**:
    ```sh
    docker-compose up
    ```

### Manual Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/hamster-bot-manager.git
    cd hamster-bot-manager
    ```

2. **Create a virtual environment and activate it**:
    ```sh
    python -m venv venv
    source venv/bin/activate
    ```

3. **Install the dependencies**:
    ```sh
    pip install poetry
    poetry install
    ```

4. **Create a `.env` file**:
    ```sh
    cp .env.example .env
    ```
   Fill in your API credentials and other configuration settings in the `.env` file.

5. **Run the application**:
    ```sh
    poetry run python main.py
    ```

## Configuration

The application is configured using environment variables defined in the `.env` file. Below is an example configuration
with detailed descriptions of each parameter:

```ini
# API credentials
API_ID = your_api_id               # Your Telegram API ID
API_HASH = your_api_hash           # Your Telegram API hash

# Directory for session files
SESSION_DIRECTORY = ./sessions     # Directory to store session files

# Energy and tapping configurations
MIN_AVAILABLE_ENERGY = 250         # Minimum available energy before taking action
SEND_TAPS_COOLDOWN = [15,25]       # Cooldown time range between taps in seconds (min, max)
SEND_TAPS_WAIT = [30,60]           # Wait time range between tap sequences in seconds (min, max)
SEND_TAPS_COUNT = [150,250]        # Number of taps to send per action (min, max)

# Level and upgrade settings
MAX_LEVEL_BOOST = 5                # Maximum level for boosts
APPLY_DAILY_ENERGY = True          # Whether to apply daily energy boost
AUTO_UPGRADE = False               # Automatically upgrade items if possible
MAX_LEVEL_UPGRADE = 15             # Maximum level for upgrades

# Retry settings
MAX_RETRIES = 3                    # Maximum number of retry attempts
RETRY_DELAY = 5                    # Delay between retries in seconds
```

## Usage

Run the HAMSTER BOT Manager using the following commands:

- **Create a new session**:
    ```sh
    python main.py --create-session your_session_name
    ```

- **List all sessions**:
    ```sh
    python main.py --list-sessions
    ```

- **Delete a session**:
    ```sh
    python main.py --delete-session your_session_name
    ```

- **Run the bot for all sessions**:
    ```sh
    python main.py --run-bot
    ```

## Development

### Project Structure

- `main.py`: Entry point of the application.
- `src/core/`: Core settings and configurations.
- `src/tapper/`: Contains the `Tapper` class which interacts with the game.
- `managers/session_manager.py`: Manages the session files.

### Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.