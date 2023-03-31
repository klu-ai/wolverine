import asyncio
import aiohttp
from bs4 import BeautifulSoup
from colorama import Fore, Style

def get_colored_text(text, color):
    return f"{color}{text}{Style.RESET_ALL}"

async def get_contribution_count(session, profile_url):
    async with session.get(profile_url) as response:
        text = await response.text()
        soup = BeautifulSoup(text, 'html.parser')
        contribution_text = soup.find('h2', class_='f4 text-normal mb-2').text.strip()
        contribution_count = int(contribution_text.split()[0].replace(',', ''))
        return contribution_count

async def get_most_active_coders(repo_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(repo_url) as response:
            repo_data = await response.json()
        
        contributors_url = repo_data['contributors_url']
        async with session.get(contributors_url) as response:
            contributors = await response.json()
        
        activity_scores = []
        tasks = []
        for contributor in contributors:
            profile_url = contributor['html_url']
            task = asyncio.ensure_future(get_contribution_count(session, profile_url))
            tasks.append(task)
        
        for i, task in enumerate(asyncio.as_completed(tasks)):
            contribution_count = await task
            contributor = contributors[i]
            activity_scores.append((contributor['login'], contribution_count))
            print(get_colored_text(f"Progress: {i+1}/{len(contributors)}", Fore.YELLOW))
        
        activity_scores.sort(key=lambda x: x[1], reverse=True)
    
    return activity_scores

repo_url = "https://api.github.com/repos/hwchase17/langchain"

async def main():
    most_active_coders = await get_most_active_coders(repo_url)

    print(get_colored_text("Most active coders:", Fore.GREEN))
    for coder, score in most_active_coders:
        print(get_colored_text(f"{coder}: {score}", Fore.CYAN))

asyncio.run(main())