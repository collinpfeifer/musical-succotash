import json
from time import sleep
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pprint import pprint as pp

# Set up Chrome options and capabilities
options = Options()
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

# Initialize the WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)


def process_browser_logs_for_network_events(logs):
    """
    Return only logs which have a method that start with "Network.response", "Network.request", or "Network.webSocket"
    since we're interested in the network events specifically.
    """
    for entry in logs:
        log = json.loads(entry["message"])["message"]
        if (
            "Network.response" in log["method"]
            or "Network.request" in log["method"]
            or "Network.webSocket" in log["method"]
        ):
            yield log


# Open the target URL
driver.get("https://www.psychologytoday.com/us/therapists/46280")

sleep(2)
# Retrieve and process network logs
therapist_uuids = []
while True:
    try:
        logs = driver.get_log("performance")
        events = process_browser_logs_for_network_events(logs)
        for event in events:
            request = event['params'].get('request', {})
            if request.get("method") == "POST" and request.get("url") == "https://www.psychologytoday.com/api/metrics/profile" and request.get("hasPostData"):
                request_data = json.loads(request.get("postData"))
                if request_data.get("metric_name") == "Impression":
                    therapist_uuids.extend(request_data.get("entity_uuids"))
        sleep(random.uniform(1, 3))
        pp(driver.find_element(By.CSS_SELECTOR,"div.pagination-controls-end a.page-btn").click())
        sleep(random.uniform(1, 3))
    except Exception as e:
        print(f"Error retrieving or processing logs: {e}")
        break

print(len(therapist_uuids))
# Quit the WebDriver
driver.quit()

def load_user_agents(uafile="psychology_today/user_agents.txt"):
	"""
	uafile : string
		path to text file of user agents, one per line
	"""
	uas = []
	with open(uafile, "rb") as uaf:
	   for ua in uaf.readlines():
		   if ua:
			   uas.append(ua.strip()[1:-1-1])
	random.shuffle(uas)
	return uas


def load_proxies(proxy_file="psychology_today/good_proxies.txt"):
    proxies = []
    with open(proxy_file, "rb") as pfile:
        for p in pfile.readlines():
            if p:
                proxies.append(p.strip()[1:-1-1])
    random.shuffle(proxies)
    return proxies
# load the user agents, in random order
user_agents = load_user_agents()
proxies = load_proxies()
therapists = []

# pp(requests.get("https://www.psychologytoday.com/directory-listing/listing/profile/609643ad-2c23-422f-8f12-a5520e764216?lang=en").json())
for therapist_uuid in therapist_uuids:
    psychology_today_api = f"https://www.psychologytoday.com/directory-listing/listing/profile/{therapist_uuid}?lang=en"
    proxy = {
        "http": random.choice(proxies),
    }
    headers = {
        "Connection": 'close',
        "User-Agent": random.choice(user_agents)
    }
    res = requests.get(psychology_today_api, proxies=proxy, headers=headers).json()
    # id, name, credentials, address, uuid, personal_website/out.pscyh link, education, phone_number, emails, profile_link, session_fees
    primary_location = res.get("primaryLocation", {})
    address_keys = ["addressLine1", "addressLine2", "cityName", "regionName", "postalCode", "countryCode"]
    education = res.get("education", {})
    education_keys = ["institution", "diplomaDegree"]
    listing_name = res.get("listingName")

    therapists.append({
        "id": res.get("id"),
        "uuid": res.get("uuid"),
        "name": res.get("contactName"),
        "address": " ".join([str(primary_location.get(key)) for key in address_keys]),
        "phone_number": res.get("formattedPhoneNumber"),
        "credentials": " ".join([cred.get("label") if cred.get("type") == "academic" else "" for cred in res.get("suffixes")]),
        "education": " ".join([str(education.get(key)) for key in education_keys]) if education != None else None,
        "session_fees": str(res.get("fees", {}).get("individual_session_cost")) if res.get("fees") != None else None,
        "profile_link": f"https://www.psychologytoday.com/us/therapists/{listing_name.replace(" ", "-")}/{res.get("id")}",
        "personal_website": f"https://out.psychologytoday.com/us/profile/{res.get("id")}/website-redirect" if res.get("hasWebsite") else None,
        "emails": []
    })
with open("psychology_today/therapists.json", "w", encoding="utf-8") as file:
    json.dump(therapists, file, ensure_ascii=False, indent=4)
