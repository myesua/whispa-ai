import requests
from typing import Optional, Dict, Any, List
import json
import requests.auth

class JiraResponse:
    def __init__(self, key: str, id: str, self_url: str):
        self.key = key
        self.id = id
        self.self_url = self_url

class JiraService:
    def __init__(self, base_url: str, project_key: str, issue_type_name: str = "Bug"):
        self.base_url = base_url.rstrip('/')
        self.project_key = project_key
        self.issue_type_name = issue_type_name
        self.api_url = f"{self.base_url}/rest/api/3/issue"

    def _execute_api(self, method: str, path: str, api_token: str, user_email: str, data: Optional[dict] = None) -> Dict[str, Any]:
        
        auth = requests.auth.HTTPBasicAuth(user_email, api_token)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        url = f"{self.base_url}/rest/api/3/{path.lstrip('/')}"
        
        response = requests.request(
            method,
            url,
            auth=auth,
            headers=headers,
            json=data,
        )

        if response.status_code not in [200, 201]:
            raise Exception(f"Jira API request failed ({response.status_code}): {response.text}")
        
        return response.json()

    def _create_data_uris(self, image_base64_list: List[str]) -> List[str]:
        data_uris = []
        for image_base64 in image_base64_list:
            if image_base64.startswith('data:'):
                data_uris.append(image_base64)
            else:
                data_uris.append(f"data:image/png;base64,{image_base64}")
        return data_uris

    async def create_issue(self, title: str, description: str, api_token: str, user_email: str, image_base64_list: Optional[List[str]] = None, labels: Optional[List[str]] = None) -> JiraResponse:
        
        embedded_uris = []
        if image_base64_list:
            embedded_uris = self._create_data_uris(image_base64_list)

        final_description = description
        
        if embedded_uris:
            image_embed = "\n\nh5. Attached Images (Embedded Data)\n" + "\n".join([f"!{uri}|width=500!" for uri in embedded_uris])
            final_description = f"{description}\n\n---\n{image_embed}"
        
        payload = {
            "fields": {
                "project": {
                    "key": self.project_key
                },
                "summary": title,
                "description": final_description,
                "issuetype": {
                    "name": self.issue_type_name
                },
                "labels": labels or []
            }
        }

        data = self._execute_api("POST", "/issue", api_token, user_email, data=payload)
        
        if data.get("key"):
            return JiraResponse(
                key=data["key"],
                id=data["id"],
                self_url=data["self"]
            )
        else:
            raise Exception("Failed to create Jira issue.")