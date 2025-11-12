import requests
from app.config import settings
from typing import Optional, Dict, Any, List
import json
from app.utils.image_upload import base64_to_proxy_url
from app.services.clean_up_queue import schedule_deletion

class LinearResponse:
    def __init__(self, id, identifier, title, url, state):
        self.id = id
        self.identifier = identifier
        self.title = title
        self.url = url
        self.state = state

    def to_dict(self):
        return {
            "id": self.id,
            "identifier": self.identifier,
            "title": self.title,
            "url": self.url,
            "state": self.state
        }

class LinearService:
    def __init__(self):
        self.api_url = settings.linear_api_url

    def _execute_graphql(self, query: str, variables: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        
        response = requests.post(
            self.api_url,
            headers={
                "Authorization": f"{api_key}",
                "Content-Type": "application/json",
            },
            json={"query": query, "variables": variables},
        )
        
        if response.status_code != 200:
            raise Exception(f"GraphQL request failed with status code {response.status_code}: {response.text}")
        
        data = response.json()
        if data.get("errors"):
             raise Exception("GraphQL errors occurred: " + json.dumps(data["errors"]))

        return data.get("data", {})
        
    async def create_issue(self, title: str, description: str, team_id: str, priority: int = 1, label_ids: list = None, api_key: str = None, image_base64_list: Optional[List[str]] = None) -> LinearResponse:
        
        uploaded_files: List[Dict[str, str]] = []
        
        try:
            if image_base64_list:
                for base64_data in image_base64_list:
                    
                    if base64_data.startswith("data:"):
                        cleaned_base64 = base64_data.split(",", 1)[-1]
                    else:
                        cleaned_base64 = base64_data

                    proxy_url, file_path = await base64_to_proxy_url(cleaned_base64)
                    
                    uploaded_files.append({
                        "url": proxy_url,
                        "file_path": file_path
                    })
            
            final_description = description
            
            uploaded_urls = [f["url"] for f in uploaded_files]

            if uploaded_urls:
                image_markdown = "\n\n### Attached Screenshots\n" + "\n".join([f"![Attachment {i+1}]({url})" for i, url in enumerate(uploaded_urls)])
                final_description = f"{description}\n\n---\n{image_markdown}"

            mutation = """
            mutation CreateIssue(
                $title: String!,
                $description: String!,
                $teamId: String!,
                $priority: Int!,
                $labelIds: [String!]
            ) {
                issueCreate(input: {
                    title: $title,
                    description: $description,
                    teamId: $teamId,
                    priority: $priority,
                    labelIds: $labelIds
                }) {
                    success
                    issue {
                        id
                        identifier
                        title
                        url
                        state {
                            name
                        }
                    }
                }
            }
            """

            variables = {
                "title": title,
                "description": final_description,
                "teamId": team_id,
                "priority": priority,
                "labelIds": label_ids or [],
            }

            data = self._execute_graphql(mutation, variables, api_key)

            if data.get("issueCreate", {}).get("success"):
                issue_data = data["issueCreate"]["issue"]
                response = LinearResponse(
                    id=issue_data["id"],
                    identifier=issue_data["identifier"],
                    title=issue_data["title"],
                    url=issue_data["url"],
                    state=issue_data["state"]
                )
                return response
            else:
                raise Exception("Failed to create issue.")
        
        finally:
            for file_info in uploaded_files:
                print('file_info: ', file_info)
                schedule_deletion(file_info["file_path"])
                # await delete_temp_file(file_info["file_path"])