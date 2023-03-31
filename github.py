import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from colorama import Fore, Style

# Function to wrap text with color escape codes
def get_colored_text(text, color):
    return f"{color}{text}{Style.RESET_ALL}"

# Function to fetch the content of a URL as text using aiohttp
async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.text()

# Function to fetch the content of a URL as JSON using aiohttp
async def fetch_json(session, url):
    async with session.get(url) as response:
        return await response.json()

# Function to get the contribution count from a user's profile page
async def get_contribution_count(session, profile_url):
    html = await fetch_url(session, profile_url)
    soup = BeautifulSoup(html, 'html.parser')
    contribution_text = soup.find('h2', class_='f4 text-normal mb-2').text.strip()
    contribution_count = int(contribution_text.split()[0].replace(',', ''))
    return contribution_count

# Function to fetch the list of contributors for a given repository
async def fetch_contributors(session, repo_url):
    repo_data = await fetch_json(session, repo_url)
    contributors_url = repo_data['contributors_url']
    return await fetch_json(session, contributors_url)

# Function to get the activity scores for a list of contributors
async def get_activity_scores(session, contributors):
    tasks = [get_contribution_count(session, contributor['html_url']) for contributor in contributors]
    contribution_counts = await asyncio.gather(*tasks)
    return [(contributor['login'], count) for contributor, count in zip(contributors, contribution_counts)]

# Function to get the most active coders for a given repository
async def get_most_active_coders(repo_url):
    async with aiohttp.ClientSession() as session:
        contributors = await fetch_contributors(session, repo_url)
        activity_scores = await get_activity_scores(session, contributors)
        activity_scores.sort(key=lambda x: x[1], reverse=True)
    return activity_scores

# Function to print the most active coders in a colored format
async def print_most_active_coders(most_active_coders):
    print(get_colored_text("Most active coders:", Fore.GREEN))
    for coder, score in most_active_coders:
        print(get_colored_text(f"{coder}: {score}", Fore.CYAN))

# Main function to run the script
async def main():
    repo_url = "https://api.github.com/repos/hwchase17/langchain"
    most_active_coders = await get_most_active_coders(repo_url)
    await print_most_active_coders(most_active_coders)

# Run the main function using asyncio
asyncio.run(main())