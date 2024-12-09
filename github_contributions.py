import os
import requests
import csv
import dateutil.parser

# Set up your token and headers
TOKEN = os.environ["GITHUB_TOKEN"]
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Define variables
variables = {"username": os.environ["GITHUB_USER"]}

# GraphQL query
query = """
query ($username: String!) {
  user(login: $username) {
    contributionsCollection {
      pullRequestReviewContributions(first: 100) {
        nodes {
          occurredAt
          pullRequest {
            title
            url
            repository {
              nameWithOwner
            }
          }
        }
      }
      commitContributionsByRepository(maxRepositories: 50) {
        repository {
          nameWithOwner
        }
        contributions(first: 100) {
          nodes {
            occurredAt
            commitCount
          }
        }
      }
      pullRequestContributionsByRepository(maxRepositories: 50) {
        repository {
          nameWithOwner
        }
        contributions(first: 100) {
          nodes {
            occurredAt
            pullRequest {
              title
              url
            }
          }
        }
      }
      issueContributionsByRepository(maxRepositories: 50) {
        repository {
          nameWithOwner
        }
        contributions(first: 100) {
          nodes {
            occurredAt
            issue {
              title
              url
            }
          }
        }
      }
    }
  }
}
"""

# Send the request
response = requests.post(
    "https://api.github.com/graphql",
    json={"query": query, "variables": variables},
    headers=HEADERS
)

if response.status_code == 200:
    data = response.json()
    contributions = []

    # Process Pull Request Reviews
    for review in data['data']['user']['contributionsCollection']['pullRequestReviewContributions']['nodes']:
        time= dateutil.parser.isoparse(review["occurredAt"])
        contributions.append({
            "type": "Code Review",
            "date":  review["occurredAt"],
            "month": time.month,
            "repo": review["pullRequest"]["repository"]["nameWithOwner"],
            "count": 1
        })

    # Process other contributions (Commits, PRs, Issues)
    for category, label in [
        ('commitContributionsByRepository', 'Commit'),
        ('pullRequestContributionsByRepository', 'Pull Request'),
        ('issueContributionsByRepository', 'Issue'),
    ]:
        for repo in data['data']['user']['contributionsCollection'][category]:
            repo_name = repo['repository']['nameWithOwner']
            for contribution in repo['contributions']['nodes']:
                time = dateutil.parser.isoparse(contribution["occurredAt"])

                contribution_data = {
                    "repo": repo_name,
                    "type": label,
                    "date":  contribution["occurredAt"],
                    "month": time.month,
                }
                if "commitCount" in contribution:
                    contribution_data["count"] = contribution['commitCount']
                elif "pullRequest" in contribution:
                    contribution_data[
                        "count"] = 1
                elif "issue" in contribution:
                    contribution_data[
                        "count"] = 1
                contributions.append(contribution_data)

    # Save to CSV
    csv_file = "github_contributions.csv"
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["date", "month", "type", "repo", "count"])
        writer.writeheader()
        writer.writerows(contributions)

    print(f"Contributions saved to {csv_file}")

else:
    print(f"Error: {response.status_code}, {response.text}")