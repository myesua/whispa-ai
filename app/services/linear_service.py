import requests
from app.config import settings
from typing import Optional, Dict, Any
import base64

class LinearResponse:
    id: str
    identifier: str
    title: str
    url: str
    state: Dict[str, str]

class LinearService:
    def __init__(self):
        self.api_url = settings.linear_api_url
        self.api_attachement = settings.linear_attachment_url
    def upload_attachment(self, file_name: str, image_base64: str, linear_api_key: str = None) -> Dict[str, Any]:
        """
        Uploads a single Base64 image directly to Linear's attachment endpoint.
        The image is processed and stored by Linear, not on our server.
        """
        if image_base64.startswith('data:'):
            header, encoded = image_base64.split(',', 1)
        else:
            encoded = image_base64
            
        try:
            image_bytes = base64.b64decode(encoded)
        except Exception:
            raise ValueError("Invalid Base64 string provided for attachment.")

        url = self.api_attachement
        files = {
            'file': (file_name, io.BytesIO(image_bytes), 'image/png')
        }
        headers = {
            "Authorization": f"{linear_api_key}",
        }
        print(f"Uploading attachment {file_name} directly to Linear...")

        # # MOCK/REAL API CALL
        # if self.api_key == settings.linear_api_key:
        #      return {
        #         "success": True,
        #         "attachmentId": f"ATT_{file_name.replace('.', '_')}_{os.urandom(4).hex()}",
        #         "url": f"https://linear.app/attachment-mock/{file_name}"
        #     }
        
        response = requests.post(url, headers=headers, files=files)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Linear Attachment upload failed ({response.status_code}): {response.text}")
    def create_issue(self, title: str, description: str, team_id: str, priority: int = 1, label_ids: list = None, linear_api_key: str = None, image_base64: Optional[str] = None, attachment_urls: Optional[list] = None) -> LinearResponse:
        print(f"Creating issue with title: {title}, description: {description}, team_id: {team_id}, priority: {priority}, label_ids: {label_ids}, image_presence: {bool(image_base64)}, attachment_urls: {attachment_urls}")
        """
        Create an issue in Linear via API.

        Args:
            title (str): The title of the issue.
            description (str): The description of the issue.
            team_id (str): The ID of the team where the issue will be created.
            priority (int): The priority of the issue (1 = high, 2 = medium, 3 = low).
            label_ids (list, optional): A list of label IDs to associate with the issue.
            linear_api_key (str, optional): The Linear API key for authentication.
            image_base64 (str, optional): Base64-encoded image data to include in the issue description.
            attachment_urls (list, optional): A list of attachment URLs to include in the issue description.

        Returns:
            dict: The created issue's details.
        """
        
        final_description = description
        if image_base64:
            image_markdown = f"![Captured Image]({image_base64})"
            final_description = f"{image_markdown}\n\n---\n\n{description}"
        
        if attachment_urls:
            image_markdown = "\n\n### Attached Screenshots\n" + "\n".join([f"![Attachment {i+1}]({url})" for i, url in enumerate(attachment_urls)])
            final_description = (
                f"Attachments included below the notes.\n\n---\n\n"
                f"{description}" 
                f"{image_markdown}" 
            )

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

        response = requests.post(
            self.api_url,
            headers={
            "Authorization": f"{linear_api_key}",
            "Content-Type": "application/json",
        },
            json={"query": mutation, "variables": variables},
        )

        if response.status_code == 200:
            data = response.json()
            print('data#: ', data)
            if data.get("data", {}).get("issueCreate", {}).get("success"):
                return data["data"]["issueCreate"]["issue"]
            else:
                raise Exception("Failed to create issue: " + str(data.get("errors", [])))
        else:
            raise Exception(f"GraphQL request failed with status code {response.status_code}: {response.text}")