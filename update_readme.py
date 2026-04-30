import requests
import re

USERNAME = "h00yaday"
API_URL = f"https://api.github.com/users/{USERNAME}/repos?sort=updated&per_page=5"

def get_latest_projects():
    response = requests.get(API_URL)
    repos = response.json()
    
    markdown_content = ""
    for repo in repos:
        if repo['name'] == USERNAME:
            continue
            
        name = repo['name']
        url = repo['html_url']
        desc = repo.get('description', 'Нет описания') or 'Нет описания'
        lang = repo.get('language', 'Unknown') or 'Unknown'
        
        markdown_content += f"- [**{name}**]({url}) — {desc} `[{lang}]`\n"
        
    return markdown_content

def update_readme(new_content):
    with open("README.md", "r", encoding="utf-8") as file:
        readme_data = file.read()

    pattern = r"(?<=<!-- PROJECTS:START -->\n).*?(?=\n<!-- PROJECTS:END -->)"
    updated_readme = re.sub(pattern, new_content, readme_data, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as file:
        file.write(updated_readme)

if __name__ == "__main__":
    projects_md = get_latest_projects()
    update_readme(projects_md)
    print("README успешно обновлен!")
