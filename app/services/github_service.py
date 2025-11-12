import requests
from typing import Optional, Dict, Any, List
import json

class GitHubResponse:
    def __init__(self, url: str, html_url: str, number: int, title: str, body: str):
        self.url = url
        self.html_url = html_url
        self.number = number
        self.title = title
        self.body = body

class GitHubService:
    def __init__(self, owner: str, repo: str):
        self.owner = owner
        self.repo = repo
        self.api_base_url = "https://api.github.com"
        self.api_url = f"{self.api_base_url}/repos/{owner}/{repo}"

    def _execute_api(self, method: str, path: str, api_key: str, data: Optional[dict] = None) -> Dict[str, Any]:
        headers = {
            "Authorization": f"token {api_key}",
            "Accept": "application/vnd.github.v3+json"
        }
        if method in ["POST", "PATCH"]:
            headers["Content-Type"] = "application/json"

        url = f"{self.api_url}{path}"
        
        response = requests.request(
            method,
            url,
            headers=headers,
            json=data,
        )

        if response.status_code not in [200, 201]:
            raise Exception(f"GitHub API request failed ({response.status_code}): {response.text}")
        
        return response.json()

    def _create_markdown_urls(self, image_base64_list: List[str]) -> List[str]:
        base64_urls = []
        for image_base64 in image_base64_list:
            if image_base64.startswith('data:'):
                base64_urls.append(image_base64)
            else:
                base64_urls.append(f"data:image/png;base64,{image_base64}")
        return base64_urls

    async def create_issue(self, title: str, description: str, api_key: str, label_names: Optional[List[str]] = None, image_base64_list: Optional[List[str]] = None) -> GitHubResponse:
        
        embedded_urls = []
        if image_base64_list:
            embedded_urls = self._create_markdown_urls(image_base64_list)

        final_description = description
        
        if embedded_urls:
            image_markdown = "\n\n### Attached Images (Embedded Data)\n" + "\n".join([f"![Attachment {i+1}]({url})" for i, url in enumerate(embedded_urls)])
            final_description = f"{description}\n\n---\n{image_markdown}"

        payload = {
            "title": title,
            "body": final_description,
            "labels": label_names or []
        }

        data = self._execute_api("POST", "/issues", api_key, data=payload)
        
        if data.get("id"):
            return GitHubResponse(
                url=data["url"],
                html_url=data["html_url"],
                number=data["number"],
                title=data["title"],
                body=data["body"]
            )
        else:
            raise Exception("Failed to create GitHub issue.")