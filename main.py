import os
from composio_langchain import ComposioToolSet, App
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from github import Github
import tempfile
from dotenv import load_dotenv

load_dotenv()

class GitHubPullRequestReviewer:
    def __init__(self):
        self.github = Github(os.environ["GITHUB_TOKEN"])
        self.llm = OpenAI(model="gpt-4")

    def get_repository(self, repo_name):
        try:
            return self.github.get_repo(repo_name)
        except Exception as e:
            raise ValueError(f"Repository not found: {repo_name}")

    def fetch_pr_details(self, repo_name, pr_number):
        repo = self.get_repository(repo_name)
        try:
            pr = repo.get_pull(pr_number)
            return {
                'title': pr.title,
                'body': pr.body,
                'files': list(pr.get_files()),
                'diff_url': pr.diff_url
            }
        except Exception as e:
            raise ValueError(f"Failed to fetch PR #{pr_number}: {str(e)}")

    def review_pr(self, repo_name, pr_number):
        try:
            pr_details = self.fetch_pr_details(repo_name, pr_number)
            repo = self.get_repository(repo_name)
            pr = repo.get_pull(pr_number)
            
            # Analyze PR content
            review_comment = self._analyze_pr(pr_details)
            
            # Post review
            pr.create_review(
                body=review_comment,
                event='COMMENT'
            )
            return review_comment
        except Exception as e:
            raise ValueError(f"Failed to review PR: {str(e)}")

    def _analyze_pr(self, pr_details):
        # Basic review template
        review = f"""
## PR Review

### Title: {pr_details['title']}

### Changes Overview:
{self._summarize_changes(pr_details['files'])}

### Recommendations:
- Code follows standard conventions
- Changes are well-documented
- Tests are included where necessary
        """
        return review

    def _summarize_changes(self, files):
        summary = []
        for file in files:
            summary.append(f"- {file.filename}: {file.additions} additions, {file.deletions} deletions")
        return "\n".join(summary)

def main():
    reviewer = GitHubPullRequestReviewer()
    try:
        repo_name = "lpintoamsys/simplehtml"  # Replace with actual repository name
        pr_number = 2  # Replace with actual PR number
        review = reviewer.review_pr(repo_name, pr_number)
        print("Review generated successfully:")
        print(review)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()