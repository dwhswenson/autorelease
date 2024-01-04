import requests
import string

GITHUB_API_ENDPOINT = "https://api.github.com/graphql"

class QueryRunner:
    def __init__(self, query_template, auth,
                 api_endpoint=GITHUB_API_ENDPOINT):
        self.query_template = string.Template(query_template)
        self.auth = auth
        self.api_endpoint = api_endpoint

    def __call__(self, **kwargs):
        query = self.query_template.substitute(**kwargs)
        return requests.post(self.api_endpoint, json={'query': query},
                             auth=self.auth).json()
