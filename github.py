import requests
import json
from bs4 import BeautifulSoup

def get_contribution_count(profile_url):
    response = requests.get(profile_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    contribution_graph = soup.find('svg', class_='js-calendar-graph-svg')
    contributions = [int(rect['data-count']) for rect in contribution_graph.find_all('rect')]
    return sum(contributions)

def get_most_active_coders(repo_url):
    response = requests.get(repo_url)
    repo_data = json.loads(response.text)
    
    contributors_url = repo_data['contributors_url']
    contributors_response = requests.get(contributors_url)
    contributors = json.loads(contributors_response.text)
    
    activity_scores = []
    for contributor in contributors:
        profile_url = contributor['html_url']
        contribution_count = get_contribution_count(profile_url)
        activity_scores.append((contributor['login'], contribution_count))
    
    activity_scores.sort(key=lambda x: x[1], reverse=True)
    
    return activity_scores

repo_url = "https://api.github.com/repos/hwchase17/langchain"
most_active_coders = get_most_active_coders(repo_url)

print("Most active coders:")
for coder, score in most_active_coders:
    print(f"{coder}: {score}")