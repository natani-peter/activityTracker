import argparse
import requests
import json
import sys
import redis

my_parser = argparse.ArgumentParser("GitHub Activity Tracker")
my_parser.add_argument("-u", "--username", help="GitHub username", required=False, default="")
username = my_parser.parse_args().username
endpoint = f'https://api.github.com/users/{username}/events'
r = redis.Redis(host='localhost', port=6379, db=0)


def cache_data(key, value, expiration=60):
    r.setex(key, expiration, json.dumps(value))


def get_cached_data(key):
    data = r.get(key)
    if data:
        return json.loads(data)
    return None


def fetch_github_events(key):
    data = get_cached_data(key)
    if data:
        print("Data From Cache")
        return data

    data = requests.get(endpoint).json()

    if data:
        print("Data From Internet")
        cache_data(key=key, value=data)
        return data


def display_events(all_events, batch_size=10):
    for i in range(0, len(all_events), batch_size):
        batch = all_events[i:i + batch_size]
        for event in batch:
            print(f"Event: {event['type']} - Repo: {event['repo']['name']}")
        if i + batch_size < len(all_events):
            print("\nPress Enter to see more, or any other key to exit.")
            if sys.stdin.read(1) != '\n':
                print("Exiting.")
                break


results_events = fetch_github_events(username)

if results_events:
    print("Latest 10 Events:")
    display_events(results_events)
else:
    print("No events found or failed to fetch data.")
