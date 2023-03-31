import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from colorama import Fore, Style
from datetime import datetime

def get_colored_text(text, color):
    return f"{color}{text}{Style.RESET_ALL}"

async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.text()

async def fetch_json(session, url):
    async with session.get(url) as response:
        return await response.json()

async def get_contribution_count(session, profile_url):
    html = await fetch_url(session, profile_url)
    soup = BeautifulSoup(html, 'html.parser')
    contribution_text = soup.find('h2', class_='f4 text-normal mb-2').text.strip()
    contribution_count = int(contribution_text.split()[0].replace(',', ''))
    return contribution_count

async def fetch_contributors(session, repo_url):
    repo_data = await fetch_json(session, repo_url)
    contributors_url = repo_data['contributors_url']
    return await fetch_json(session, contributors_url)

async def get_activity_scores(session, contributors):
    tasks = [get_contribution_count(session, contributor['html_url']) for contributor in contributors]
    contribution_counts = await asyncio.gather(*tasks)
    return [(contributor['login'], count, contributor['html_url']) for contributor, count in zip(contributors, contribution_counts)]

async def get_most_active_coders(repo_url):
    async with aiohttp.ClientSession() as session:
        contributors = await fetch_contributors(session, repo_url)
        activity_scores = await get_activity_scores(session, contributors)
        activity_scores.sort(key=lambda x: x[1], reverse=True)
    return activity_scores

async def print_most_active_coders(most_active_coders):
    print(get_colored_text("Most active coders:", Fore.GREEN))
    for coder, score, url in most_active_coders:
        print(get_colored_text(f"{coder}: {score} - {url}", Fore.CYAN))

def save_output_to_md_file(most_active_coders):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"most_active_coders_{timestamp}.md"
    
    with open(filename, 'w') as file:
        file.write("# Most active coders\n\n")
        for coder, score, url in most_active_coders:
            file.write(f"- {coder}: {score} - {url}\n")

async def main():
    repo_url = "https://api.github.com/repos/{owner}/{repo}"
    most_active_coders = await get_most_active_coders(repo_url)
    await print_most_active_coders(most_active_coders)
    save_output_to_md_file(most_active_coders)

asyncio.run(main())