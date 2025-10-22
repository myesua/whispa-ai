import requests
from app.config import settings

class LinearResponse:
    id: str
    identifier: str
    title: str
    url: str
    state: {"name": str}

class LinearService:
    def __init__(self):
        self.api_url = settings.linear_api_url
        self.headers = {
            "Authorization": f"{settings.linear_api_key}",
            "Content-Type": "application/json",
        }

    def create_issue(self, title: str, description: str, team_id: str, priority: int = 1, label_ids: list = None) -> LinearResponse:
        print(f"Creating issue with title: {title}, description: {description}, team_id: {team_id}, priority: {priority}, label_ids: {label_ids}")
        """
        Create an issue in Linear via API.

        Args:
            title (str): The title of the issue.
            description (str): The description of the issue.
            team_id (str): The ID of the team where the issue will be created.
            priority (int): The priority of the issue (1 = high, 2 = medium, 3 = low).
            label_ids (list, optional): A list of label IDs to associate with the issue.

        Returns:
            dict: The created issue's details.
        """
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
            "description": description,
            "teamId": team_id,
            "priority": priority,
            "labelIds": label_ids or [],
        }

        response = requests.post(
            self.api_url,
            headers=self.headers,
            json={"query": mutation, "variables": variables},
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("data", {}).get("issueCreate", {}).get("success"):
                return data["data"]["issueCreate"]["issue"]
            else:
                raise Exception("Failed to create issue: " + str(data.get("errors", [])))
        else:
            raise Exception(f"GraphQL request failed with status code {response.status_code}: {response.text}")