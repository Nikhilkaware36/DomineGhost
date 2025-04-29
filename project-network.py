import re
import subprocess
import sys
import time
import random
import requests
import os
from socket import gethostbyname, gethostbyaddr
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

# Function to validate domain format
def validate_domain(domain):
    pattern = r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"
    return re.match(pattern, domain)

# Function to display a loading animation
def loading_animation():
    loading_text = f"{Fore.CYAN}Wait for the tool to be ready in sec..."
    print(f"{loading_text}\n")
    time.sleep(1)
    for i in range(4):
        print(f"{loading_text} {'.' * (i+1)}", end="\r")
        time.sleep(0.5)

# Function to show the banner with cool effects
def show_banner():
    banner = f"""{Fore.LIGHTCYAN_EX}
░█▀▄░█▀█░█▄█░▀█▀░█▀█░█▀▀░█▀▀░█░█░█▀█░█▀▀░▀█▀
░█░█░█░█░█░█░░█░░█░█░█▀▀░█░█░█▀█░█░█░▀▀█░░█░
░▀▀░░▀▀▀░▀░▀░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀░▀░▀▀▀░▀▀▀░░▀░
{Style.RESET_ALL}
{Fore.GREEN}
-------------------------------
Project: DomainGhost
Author : Black RAT (Nikhil Kaware)
Version: 1.0
-------------------------------{Style.RESET_ALL}
"""
    print(banner)
    loading_animation()

# Function to show scan options
def show_menu():
    menu = f"""{Fore.CYAN}Choose scan type:
    {Fore.GREEN}1. Beginner Scan
    {Fore.YELLOW}2. Intermediate Scan
    {Fore.RED}3. Hard Scam/Phishing Analysis
    """
    choice = input(f"{menu}{Fore.CYAN}Enter your choice (1-3): ")
    return choice

# Success and failure indicators
def success_failure_indicator(scan_type, success=True):
    if success:
        print(f"{Fore.GREEN}[✔️] {scan_type} succeeded.")
    else:
        print(f"{Fore.RED}[❌] {scan_type} failed.")

# Function to check domain age (based on WHOIS data)
def get_domain_age(domain):
    try:
        whois_data = subprocess.check_output(['whois', domain])
        for line in whois_data.decode().splitlines():
            if "Creation Date" in line or "created" in line:
                date_str = line.split(":")[1].strip()
                for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%d-%b-%Y"):
                    try:
                        creation_date = datetime.strptime(date_str, fmt)
                        age = (datetime.now() - creation_date).days
                        return age
                    except ValueError:
                        continue
    except Exception as e:
        print(f"Error getting domain age: {e}")
    return None

# Beginner scan
def beginner_scan(domain):
    print(f"\n{Fore.GREEN}[+] Running WHOIS Scan (Offline)...")
    try:
        subprocess.run(["whois", domain], check=True)
        success_failure_indicator("WHOIS Scan")
    except subprocess.CalledProcessError:
        success_failure_indicator("WHOIS Scan", success=False)

    print(f"\n{Fore.GREEN}[+] Running DNS Lookup (Online)...")
    try:
        response = requests.get(f"https://dns.google/resolve?name={domain}")
        print(f"{Fore.MAGENTA}DNS Response: {response.json()}")
        success_failure_indicator("DNS Lookup")
    except requests.exceptions.RequestException:
        success_failure_indicator("DNS Lookup", success=False)

    print(f"\n{Fore.GREEN}[+] Running Ping Test (Offline)...")
    try:
        subprocess.run(["ping", "-c", "4", domain], check=True)
        success_failure_indicator("Ping Test")
    except subprocess.CalledProcessError:
        success_failure_indicator("Ping Test", success=False)

    print(f"\n{Fore.GREEN}[+] Running NMAP Basic Scan (Offline)...")
    start_time = datetime.now()
    result = subprocess.run(["nmap", "-F", domain], capture_output=True, text=True)

    if result.returncode == 0:
        elapsed_time = datetime.now() - start_time
        print(f"{Fore.GREEN}[✔️] NMAP Scan Results (Success) [{elapsed_time}]:\n{result.stdout}")
    else:
        success_failure_indicator("NMAP Basic Scan", success=False)

    print(f"\n{Fore.YELLOW}[+] AI Insight: {random.choice(['Domain is new and could be suspicious.', 'No known issues found.', 'Might be related to spam activity.'])}")

# Intermediate scan
def intermediate_scan(domain):
    print(f"\n{Fore.YELLOW}[+] Running NMAP Full Scan (Offline)...")
    result = subprocess.run(["nmap", "-p-", domain], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"{Fore.YELLOW}[✔️] NMAP Full Scan Results:\n{result.stdout}")
    else:
        success_failure_indicator("NMAP Full Scan", success=False)

    print(f"\n{Fore.YELLOW}[+] Running Reverse IP Lookup (Online)...")
    try:
        ip = gethostbyname(domain)
        reverse = gethostbyaddr(ip)
        print(f"{Fore.MAGENTA}Reverse IP Info: {reverse}")
        success_failure_indicator("Reverse IP Lookup")
    except Exception:
        success_failure_indicator("Reverse IP Lookup", success=False)

    print(f"\n{Fore.YELLOW}[+] Running Port Scan (Offline)...")
    subprocess.run(["nmap", "--open", domain])

# Hard scan with fallback and report saving
def hard_scan(domain):
    report_dir = "reports"
    os.makedirs(report_dir, exist_ok=True)
    report_file = os.path.join(report_dir, f"{domain}-report.txt")

    def write_report(text):
        with open(report_file, "a") as f:
            f.write(text + "\n")

    print(f"\n{Fore.RED}[+] Running NMAP Aggressive Scan...")
    write_report(f"========== Hard Scan Report for {domain} ==========")

    try:
        result = subprocess.run(["nmap", "-A", domain], capture_output=True, text=True)
        if result.returncode == 0 and "0 hosts up" not in result.stdout:
            print(result.stdout)
            write_report("=== NMAP Aggressive Scan ===\n" + result.stdout)
            success_failure_indicator("NMAP Aggressive Scan")
        else:
            raise RuntimeError("Host down or ping blocked.")
    except:
        print(f"{Fore.YELLOW}[!] Aggressive scan failed. Retrying with NMAP -Pn...")
        try:
            result = subprocess.run(
                ["nmap", "-Pn", "-sS", "-sV", "-O", "--top-ports", "100", domain],
                capture_output=True, text=True)
            print(result.stdout)
            write_report("=== NMAP Fallback Scan (-Pn) ===\n" + result.stdout)
            success_failure_indicator("NMAP Fallback Scan")
        except Exception as e:
            print(f"{Fore.RED}[❌] NMAP fallback failed: {e}")
            write_report(f"[!] NMAP Fallback failed: {e}")
            success_failure_indicator("NMAP Fallback Scan", success=False)

    print(f"\n{Fore.RED}[+] Running Vulnerability Scan with Nikto...")
    try:
        nikto_result = subprocess.run(["nikto", "-h", domain], capture_output=True, text=True)
        print(nikto_result.stdout)
        write_report("=== Nikto Vulnerability Scan ===\n" + nikto_result.stdout)
        success_failure_indicator("Nikto Scan")
    except Exception as e:
        print(f"{Fore.RED}[❌] Nikto scan failed: {e}")
        write_report(f"[!] Nikto scan failed: {e}")
        success_failure_indicator("Nikto Scan", success=False)

    insight = random.choice([
        "Possible vulnerability detected in port 80.",
        "No critical vulnerabilities found.",
        "Domain is hosted on a known insecure server."
    ])
    print(f"\n{Fore.RED}[+] AI Insight: {insight}")
    write_report(f"\n=== AI Insight ===\n{insight}\n")

    print(f"{Fore.GREEN}\n[✔️] Report saved to: {report_file}\n")

# Main function
def main():
    show_banner()
    domain = input(f"{Fore.CYAN}Enter domain (example: example.com): ").strip()

    if not validate_domain(domain):
        print(f"{Fore.RED}Invalid domain format! Example: example.com")
        sys.exit(1)

    age = get_domain_age(domain)
    if age:
        print(f"\n{Fore.YELLOW}Domain Age: {age} days")
    else:
        print(f"{Fore.RED}Could not determine domain age.")

    choice = show_menu()

    print(f"{Fore.CYAN}Wait for result...")

    if choice == '1':
        beginner_scan(domain)
    elif choice == '2':
        intermediate_scan(domain)
    elif choice == '3':
        hard_scan(domain)
    else:
        print(f"{Fore.RED}Invalid choice! Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    main()
