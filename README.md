# 🔮 AWS-AUTOMATION

An advanced automation system for AWS services, featuring bots and scripts for various tasks with notification support.

Created and maintained by [@khadafigans](https://github.com/khadafigans)

## 🚀 Features

* ✅ Automated AWS resource management and monitoring
* ✅ Notification integration via email and Telegram
* ✅ Modular scripts organized in folders for specific functionalities
* ✅ Easy configuration through script variables
* ✅ Support for AWS SDK integration

## 📦 Requirements

Before you get started, ensure you have the following installed:

* Python 3.8 or higher
* AWS CLI (for configuring credentials: run `aws configure`)
* Pip (Python package manager)

## ⚙️ Installation

Follow these steps to get the AWS-AUTOMATION up and running:

### 1. Clone the Repository

First, clone the project to your local machine:

```
git clone https://github.com/khadafigans/AWS-AUTOMATION.git
cd AWS-AUTOMATION
```

### 2. Install Dependencies

Install the required Python libraries using pip. The core dependencies include:

- `boto3` for AWS interactions
- `requests` for API calls (if used)
- `python-telegram-bot` for Telegram notifications (if applicable)

Run:

```
pip install boto3 requests python-telegram-bot
```

Note: Additional dependencies may be required based on specific scripts. Check each script's imports for any other libraries and install them accordingly. No internet access is needed beyond pip installs; all operations are local or via AWS APIs.

## 📁 Configuration

The repository is organized into folders, each containing specific automation scripts. Check all folders and files for their purpose:

- **BOT_AWS/**: Contains the main AWS bot script.
  - `BOT_AWS.py`: The primary Python script for AWS automation with notifications.

For other potential folders (e.g., if the repo includes additional automation like instance creation, backups, etc.), review their contents similarly. Each script typically requires AWS credentials and may have custom setups.

### Specific Configuration for BOT_AWS/BOT_AWS.py

Open `BOT_AWS/BOT_AWS.py` in a text editor and configure the following variables at the top of the file:

```
email = 'your_email@example.com'  # Email address for sending notifications
telegram_bot = 'your_telegram_bot_token'  # Telegram bot API token (obtain from BotFather)
telegram_chat_id = 'your_chat_id'  # Telegram chat ID to receive notifications
```

Additionally:
- Ensure AWS credentials are configured (access key, secret key, region) via AWS CLI (`aws configure`) or environment variables.
- If the script uses other services, set any required API keys or parameters in the code.

For how to use: The script likely performs AWS tasks (e.g., monitoring resources, automating deployments) and sends alerts via email or Telegram on events.

Review the script code for exact functionality, inputs, or command-line arguments.

## 🚀 Usage

To run a script, navigate to its folder and execute it with Python.

For example, for the BOT_AWS script:

```
cd BOT_AWS
python BOT_AWS.py
```

- Ensure all dependencies are installed and configurations are set before running.
- Scripts may require running in a virtual environment (e.g., using `venv`) for isolation.
- If a script needs additional setup (e.g., environment variables), it will be commented in the code.

Repeat for other folders/scripts in the repository. Always test in a safe environment to avoid unintended AWS changes.
