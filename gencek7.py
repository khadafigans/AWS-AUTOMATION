import json
import random
import socket
from concurrent.futures import ThreadPoolExecutor
from socket import timeout
from colorama import init, Fore, Style

# Initialize colorama for Windows
init()

def load_config(config_file='config.json'):
    with open(config_file, 'r') as file:
        return json.load(file)

def generate_ip_segment(segment):
    if '##' in segment:
        range_part = segment.strip('##').split('-')
        if len(range_part) == 2:
            return str(random.randint(int(range_part[0]), int(range_part[1])))
    return segment

def generate_ip(config, used_ips):
    ip_prefix = random.choice(config['ip_prefixes'])  # Choose a random IP prefix from the list
    while True:
        parts = ip_prefix.split('.')
        ip = '.'.join(generate_ip_segment(part) for part in parts)
        if ip not in used_ips:
            used_ips.add(ip)
            return ip

def ip_to_domain(ip):
    try:
        domain = socket.gethostbyaddr(ip)
        return domain[0]
    except socket.herror:
        return "Domain not found"

def check_ip_live(ip, output_file, domain_output_file, index, total_ips, used_domains, used_ips):
    try:
        with socket.create_connection((ip, 80), timeout=1) as sock:
            domain = ip_to_domain(ip)
            with open(output_file, 'a') as f:
                f.write(f"{ip}\n")
            if domain != "Domain not found" and domain not in used_domains:
                with open(domain_output_file, 'a') as f:
                    f.write(f"{domain}\n")
                used_domains.add(domain)
            elif domain == "Domain not found" and ip not in used_ips:
                with open(domain_output_file, 'a') as f:
                    f.write(f"{ip}\n")
                used_ips.add(ip)
            print(f"{index}/{total_ips} {ip} -> {Fore.GREEN + Style.BRIGHT}LIVE{Style.RESET_ALL} -> {domain}")
            return True
    except (socket.timeout, socket.error) as e:
        print(f"{index}/{total_ips} {ip} -> {Fore.RED + Style.BRIGHT}DEAD : {str(e)}{Style.RESET_ALL}")
        return False

def main(config):
    used_ips = set()
    used_domains = set()
    ips = []
    while len(ips) < config['num_ips']:
        ip = generate_ip(config, used_ips)
        ips.append(ip)

    total_ips = len(ips)

    with ThreadPoolExecutor(max_workers=config['threads']) as executor:
        futures = [executor.submit(check_ip_live, ip, config['output_file'], config['domain_output_file'], i+1, total_ips, used_domains, used_ips) for i, ip in enumerate(ips)]

    count_live = sum(f.result() for f in futures)

    print(f"Total {count_live} IP(s) are live. Results saved in {config['output_file']} and {config['domain_output_file']}")

if __name__ == "__main__":
    config = load_config()
    main(config)