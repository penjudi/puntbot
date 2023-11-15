import asyncio
import requests
import json
import time
from threading import Timer
from bs4 import BeautifulSoup
from htmldiff import diff
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from difflib import ndiff


class WebsiteChangeDetector:
    def __init__(self, urls):
        self.urls = urls
        self.current_contents = self.get_website_contents()

    # Capture Dynamic Content: Integrate the asynchronous capture_website function into the compare_snapshots method to capture rendered content before comparison
    def compare_snapshots(self, reference_snapshot, new_snapshot):
        new_rendered_content = asyncio.get_event_loop().run_until_complete(self.capture_website(new_snapshot))
        reference_soup = BeautifulSoup(reference_snapshot, 'html.parser')
        new_soup = BeautifulSoup(new_rendered_content, 'html.parser')
        reference_elements = reference_soup.find_all()
        new_elements = new_soup.find_all()
        num_changes = 0

        for reference_elem, new_elem in zip(reference_elements, new_elements):
            if reference_elem != new_elem:
                num_changes += 1
                diff_result = diff(str(reference_elem), str(new_elem))
                change_type = self.get_change_type(reference_elem, new_elem)
                print(f"Change detected in HTML element: {reference_elem.name}")
                print(f"Change Type: {change_type}")
                print(f"Difference: {diff_result}")

                change_details = {
                    "url": reference_elem.get("href"),  # Example: Extract affected page URL
                    "change_type": change_type,
                    "diff_result": diff_result
                }
                alert_message = self.generate_alert_message(change_details)
                self.send_alert(alert_message)

        print(f"Total changes detected: {num_changes}")

    # Establishing Baselines: Call the capture_website_content function within the __init__ method to capture and save baselines for all URLs
    def __init__(self, urls):
        self.urls = urls
        self.current_contents = self.get_website_contents()

        # Capture and save baselines for all URLs
        for url in self.urls:
            content = asyncio.get_event_loop().run_until_complete(self.capture_website(url))
            self.capture_snapshot(url, content)

    # Refining Change Detection: Replace the current compare_snapshots implementation with the detect_changes function to generate diffs and extract specific changes.
    def detect_changes(self, content, baseline):
        diff = ndiff(baseline.splitlines(), content.splitlines())
        changes = [line for line in diff if line.startswith('+') or line.startswith('-')]

        # Implement Logging: Add logging statements within the compare_snapshots method to record change details, and consider implementing a separate logging function for general notifications.
        for line in changes:
            if line.startswith('+'):
                change_type = "Addition"
                change_content = line[1:]
            else:
                change_type = "Removal"
                change_content = line[2:]

            logging.info(f"Change detected: {change_type} - {change_content}")

        return changes

    def get_website_content(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return None

    def get_website_contents(self):
        contents = {}
        for url in self.urls:
            content = self.get_website_content(url)
            if content is not None:
                contents[url] = content
            else:
                contents[url] = None
        return contents

    def detect_website_changes(self):
        new_contents = self.get_website_contents()
        for url, new_content in new_contents.items():
            current_content = self.current_contents[url]
            if new_content is not None:
                if new_content != current_content:
                    print(f"Website {url} content has changed!")
                    self.current_contents[url] = new_content
                    self.capture_snapshot(url, new_content)
                    self.compare_snapshots(current_content, new_content)
                else:
                    print(f"Website {url} content has not changed.")
            else:
                print(f"Failed to retrieve website {url} content.")

    def compare_snapshots(self, reference_snapshot, new_snapshot):
        reference_soup = BeautifulSoup(reference_snapshot, 'html.parser')
        new_soup = BeautifulSoup(new_snapshot, 'html.parser')
        reference_elements = reference_soup.find_all()
        new_elements = new_soup.find_all()
        num_changes = 0

        for reference_elem, new_elem in zip(reference_elements, new_elements):
            if reference_elem != new_elem:
                num_changes += 1
                diff_result = diff(str(reference_elem), str(new_elem))
                change_type = self.get_change_type(reference_elem, new_elem)
                print(f"Change detected in HTML element: {reference_elem.name}")
                print(f"Change Type: {change_type}")
                print(f"Difference: {diff_result}")

                change_details = {
                    "url": reference_elem.get("href"),  # Example: Extract affected page URL
                    "change_type": change_type,
                    "diff_result": diff_result
                }
                alert_message = self.generate_alert_message(change_details)
                self.send_alert(alert_message)

        print(f"Total changes detected: {num_changes}")

    def get_change_type(self, reference_elem, new_elem):
        if reference_elem.name != new_elem.name:
            return "Layout Modification"
        else:
            return "Data Element Change"

    def capture_snapshot(self, url, content):
        snapshot = {
            "url": url,
            "content": content
        }
        # You can choose to store the snapshot in a JSON file or a database
        with open("snapshots.json", "a") as file:
            file.write(json.dumps(snapshot) + "\n")

    def capture_snapshots(self, urls):
        for url in urls:
            content = self.get_website_content(url)
            if content is not None:
                self.capture_snapshot(url, content)
                print(f"Snapshot captured for website: {url}")
            else:
                print(f"Failed to retrieve website content for: {url}")

    def schedule_capture_snapshots(self, interval):
        self.capture_snapshots(self.urls)
        Timer(interval, self.schedule_capture_snapshots, (interval,)).start()

    def generate_alert_message(self, change_details):
        url = change_details["url"]
        change_type = change_details["change_type"]
        diff_result = change_details["diff_result"]

        # Create an alert message with relevant information
        alert_message = f"Change detected in the website:\n\n"
        alert_message += f"Affected Page: {url}\n"
        alert_message += f"Change Type: {change_type}\n"
        alert_message += f"Difference:\n{diff_result}\n"

        return alert_message

    def send_alert(self, alert_message):
        recipient_email = "jackercrack@yahoo.com"

        # Send email alert
        email_subject = "Website Change Detected"
        email_body = alert_message
        self.send_email(recipient_email, email_subject, email_body)

        # Store alert in log file
        self.store_in_log(alert_message)

    def send_email(self, recipient_email, subject, body):
        # Email configuration
        sender_email = "your-email@example.com"
        smtp_server = "smtp.example.com"
        smtp_port = 587
        smtp_username = "your-username"
        smtp_password = "your-password"

        # Create message container
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject

        # Add body to the message
        message.attach(MIMEText(body, "plain"))

        # Send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(message)

    def store_in_log(self, alert_message):
        # Store the alert message in a log file for future reference
        with open("alert_log.txt", "a") as file:
            file.write(alert_message + "\n")

#Handling Dynamic Content
async def capture_website(url):
    browser = await launch()
    page = await browser.newPage()
    await page.goto(url)
    await page.waitForSelector('body')
    content = await page.content()
    await browser.close()
    return content

#Establishing Baselines
# Assuming you have a function to capture the website content
def capture_website_content(url):
    # Capture the website content
    content = ...

    # Save the content as a baseline for comparison
    save_baseline(content)

#Refining Change Detection
def detect_changes(content, baseline):
    diff = difflib.ndiff(baseline.splitlines(), content.splitlines())
    changes = [line for line in diff if line.startswith('+') or line.startswith('-')]
    return changes

# Usage
content = capture_website_content('https://example.com')
baseline = load_baseline()
changes = detect_changes(content, baseline)

# Usage
url = 'https://example.com'
rendered_content = asyncio.get_event_loop().run_until_complete(capture_website(url))

# Example usage
if __name__ == "__main__":
    urls = ["https://www.punters.com.au/", "https://www.racingqueensland.com.au/", "https://www.oddschecker.com/", "https://www.bet365.com.au/", "https://www.ladbrokes.com.au/", "https://www.skyracingworld.com/", "https://www.racingandsports.com.au/", "https://www.thegreyhoundrecorder.com.au/", "https://www.harness.org.au/", "https://www.racing.com/", "https://racingaustralia.horse/", "https://www.thetrots.com.au/"]
    detector = WebsiteChangeDetector(urls)
    detector.detect_website_changes()
    interval = 3600  # Capture snapshots every 1 hour (3600 seconds)
    detector.schedule_capture_snapshots(interval)
    # Keep the script running indefinitely
    while True:
        time.sleep(1)
