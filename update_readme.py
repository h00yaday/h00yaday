import requests
import re
import os

USERNAME = "h00yaday"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def get_latest_projects():
    markdown_content = ""

    if GITHUB_TOKEN:
        headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
        query = """
        query {
          user(login: "%s") {
            repositories(first: 5, orderBy: {field: PUSHED_AT, direction: DESC}, isFork: false) {
              nodes {
                name
                nameWithOwner
                url
                description
                pushedAt
                primaryLanguage { name }
              }
            }
            repositoriesContributedTo(first: 5, contributionTypes: [COMMIT, PULL_REQUEST, REPOSITORY], orderBy: {field: PUSHED_AT, direction: DESC}) {
              nodes {
                name
                nameWithOwner
                url
                description
                pushedAt
                primaryLanguage { name }
              }
            }
          }
        }
        """ % USERNAME

        response = requests.post("https://api.github.com/graphql", json={'query': query}, headers=headers)
        
        if response.status_code == 200:
            data = response.json().get('data', {}).get('user', {})
            owned = data.get('repositories', {}).get('nodes', [])
            contributed = data.get('repositoriesContributedTo', {}).get('nodes', [])
            
            all_repos = {}
            for repo in owned + contributed:
                if repo['name'] == USERNAME: 
                    continue
                all_repos[repo['nameWithOwner']] = repo
            
            repos_list = list(all_repos.values())
            repos_list.sort(key=lambda x: x.get('pushedAt', ''), reverse=True)
            
            # Берем первые 5-6 свежих проектов
            for repo in repos_list[:6]:
                name = repo['nameWithOwner'] 
                url = repo['url']
                desc = repo.get('description') or 'No description'
                lang_data = repo.get('primaryLanguage')
                lang = lang_data['name'] if lang_data else 'Unknown'
                
                markdown_content += f"- [**{name}**]({url}) — {desc} `[{lang}]`\n"
                
            return markdown_content
        else:
            print(f"Ошибка GraphQL: {response.status_code}. Переход на REST API.")

    print("Using REST API (whithout another repositories).")
    API_URL = f"https://api.github.com/users/{USERNAME}/repos?sort=updated&per_page=5"
    response = requests.get(API_URL)
    repos = response.json()
    
    for repo in repos:
        if repo['name'] == USERNAME:
            continue
            
        name = repo['full_name'] 
        url = repo['html_url']
        desc = repo.get('description') or 'No description'
        lang = repo.get('language') or 'Unknown'
        
        markdown_content += f"- [**{name}**]({url}) — {desc} `[{lang}]`\n"
        
    return markdown_content

def update_readme(new_content):
    if not new_content:
        return

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
