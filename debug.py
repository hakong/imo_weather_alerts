import requests
from urllib.parse import quote

# URL to fetch the list of alerts
list_url = "https://api.vedur.is/cap/v1/capbroker/sent/from/2023/1/1/to/2023/1/5/category/All/"

# Fetching the list of alerts
response = requests.get(list_url)
alerts_list = response.json()

# Function to parse the JSON and extract the information
def parse_alerts(json_data):
    if 'alert' in json_data:
        info_list = json_data['alert']['info']
        return [
            {
                'areaDesc': info['area']['areaDesc'],
                'category': info['category'],
                'certainty': info['certainty'],
                'description': info['description'],
                'event': info['event'],
                'headline': info['headline'],
                'onset': info['onset'],
                'severity': info['severity'],
                'urgency': info['urgency'],
                'expires': info['expires'],
                'language': info['language']
            }
            for info in info_list
        ]
    else:
        return []

# Function to construct alert URL
def construct_alert_url(sender, identifier, sent):
    base_url = "https://api.vedur.is/cap/v1/capbroker/sender/{}/identifier/{}/sent/{}/json/"
    # The sent datetime needs to be URL encoded
    encoded_sent = quote(sent)
    return base_url.format(sender, identifier, encoded_sent)

# List to hold all parsed alert details
all_alert_details = []

# Loop through each alert in the list
for alert in alerts_list:
    # Construct URL for the alert details
    alert_url = construct_alert_url(alert['sender'], alert['identifier'], alert['sent'])
    # Fetch the alert details
    alert_response = requests.get(alert_url)
    alert_data = alert_response.json()
    # Parse the fetched JSON data
    parsed_alerts = parse_alerts(alert_data)
    all_alert_details.extend(parsed_alerts)

# Display the result
for alert_detail in all_alert_details:
    print(alert_detail)
