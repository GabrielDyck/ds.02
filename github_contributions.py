import os
import requests
import csv

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
      commitContributionsByRepository(maxRepositories: 10) {
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
      pullRequestContributionsByRepository(maxRepositories: 10) {
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
      issueContributionsByRepository(maxRepositories: 10) {
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
        contributions.append({
            "type": "Code Review",
            "date": review["occurredAt"],
            "repo": review["pullRequest"]["repository"]["nameWithOwner"],
            "details": f"Reviewed PR: {review['pullRequest']['title']} ({review['pullRequest']['url']})"
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
                contribution_data = {
                    "repo": repo_name,
                    "type": label,
                    "date": contribution["occurredAt"],
                }
                if "commitCount" in contribution:
                    contribution_data["details"] = f"Commits: {contribution['commitCount']}"
                elif "pullRequest" in contribution:
                    contribution_data[
                        "details"] = f"PR: {contribution['pullRequest']['title']} ({contribution['pullRequest']['url']})"
                elif "issue" in contribution:
                    contribution_data[
                        "details"] = f"Issue: {contribution['issue']['title']} ({contribution['issue']['url']})"
                contributions.append(contribution_data)

    # Save to CSV
    csv_file = "github_contributions.csv"
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["date", "type", "repo", "details"])
        writer.writeheader()
        writer.writerows(contributions)

    print(f"Contributions saved to {csv_file}")

else:
    print(f"Error: {response.status_code}, {response.text}")