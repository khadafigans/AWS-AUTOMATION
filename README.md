# 🪐 AWS-AUTOMATION

An advanced automation system for AWS services, featuring bots and scripts for various tasks with notification support.

Created and maintained by [Bob Marley](https://github.com/khadafigans)

---

## 🚀 Features

- ✅ Automated AWS resource management and monitoring  
- ✅ Notification integration via email and Telegram  
- ✅ Modular scripts organized in folders for specific functionalities  
- ✅ Easy configuration through script variables  
- ✅ Support for AWS SDK integration  

---

## 📦 Requirements

Before you get started, ensure you have the following installed:

- Python 3.8 or higher
- AWS CLI (for configuring credentials: run `aws configure`)
- Pip (Python package manager)


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

Organize your data in the following folder structure:

```
AWS-AUTOMATION/
│
├── BOT_AWS/ # AWS Bot notifier
│   ├── BOT_AWS.py # Python bot script for AWS alerts
│   ├── console.txt # Output Console Created
│   ├── EC2.txt # Output EC2 Instances inside console
│   ├── env.txt # Output .env if available
│   ├── json.txt # Output Web
│   ├── result.txt # AWS Key Results
│   ├── run.cmd # Windows batch shortcut
│   └── ses.txt # Output SES Available
│
├── AWSCEK/ # AWS Key checker (Node.js & Python mix)
│   ├── aws.js # Main AWS key checking script (Node.js)
│   ├── aws_key.txt # Store AWS keys here (format: KEY:SECRET)
│   ├── package.json # Node.js dependencies
│   ├── package-lock.json
│   ├── result.txt # Output of AWS checks
│   └── rm_region.py # Python helper to handle AWS region cleanup
│
└── GENIP/ # IP/domain generation helper
    ├── hasil/ # Output Folder
    ├── config.json # Config for domain/IP generation
    ├── gas.cmd # Windows batch shortcut
    └── gencek7.py # Python script for generating domain/IP
```

## 🚀 Usage How to Run Each Script

### GENIP

1. Open the `GENIP` folder.
2. Edit `config.json` as needed for your AWS IP/domain generation.
3. To run the generator:
   - On Linux/macOS:
     ```bash
     python3 gencek7.py
     ```
   - On Windows:
     Double-click or run:
     ```cmd
     gas.cmd
     ```

---

### BOT_AWS

1. Open the `BOT_AWS` folder.
2. **Configure notifications (optional):**
   - Open `BOT_AWS.py` in a text editor.
   - Set your email and Telegram bot credentials at the top of the file:
   ```python
   EMAIL_SENDER = "your_email@gmail.com"
   RECIPIENT_EMAIL = "RECIPIENT_EMAIL"
   TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"
   TELEGRAM_CHAT_ID = "your_telegram_chat_id"

   # AWS default username and password
   iam_user = 'AdminEc2CNSL'
   iam_password = 'Root1337'
   ```
3. To run the main script:
   - On Linux/macOS:
     ```bash
     python3 BOT_AWS.py
     ```
   - On Windows:
     Double-click or run:
     ```cmd
     run.cmd
     ```
4. Output and results will be saved in `result.txt` and other text files in the folder.

---

### AWSCEK

1. Open the `AWSCEK` folder.
2. **Install Node.js dependencies** (if not already done):
   ```bash
   npm install
   ```
3. **To run the AWS key/SES console script:**
  ```bash
  node aws.js
  ```
4. **To run the region removal script:**
  ```bash
  python rm_region.py # can be python3 based on what you installed
  ```
5. **Output and results will be saved in result.txt and other files in the folder.**

📧 Contact :
------
You Want Ask About All My Tools Private Add Me On : 
```
[+] Telegram : @marleyybob123
[+] Telegram Channel : https://t.me/BMARLEYTOOLS
```
# This script is public and not for sale!

**Join telegram channel for more Free Tools**

           This script was made for an educational purposes only, any illegal activites will have nothing to do with me

<br>©2025 Bob Marley
</html>
