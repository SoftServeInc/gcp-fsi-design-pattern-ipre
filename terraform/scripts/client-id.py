import google.auth
import google.auth.transport.requests
import requests
import six.moves.urllib.parse
import sys
import json


# Authenticate with Google Cloud.
# See: https://cloud.google.com/docs/authentication/getting-started
credentials, _ = google.auth.default(
    scopes=['https://www.googleapis.com/auth/cloud-platform'])
authed_session = google.auth.transport.requests.AuthorizedSession(
    credentials)
query = json.loads(sys.stdin.read())
project_id = query['project_id']
location = query['location']
composer_environment = query['composer_environment']

environment_url = (
    'https://composer.googleapis.com/v1beta1/projects/{}/locations/{}'
    '/environments/{}').format(project_id, location, composer_environment)
composer_response = authed_session.request('GET', environment_url)
environment_data = composer_response.json()
airflow_uri = environment_data['config']['airflowUri']

# The Composer environment response does not include the IAP client ID.
# Make a second, unauthenticated HTTP request to the web server to get the
# redirect URI.
redirect_response = requests.get(airflow_uri, allow_redirects=False)
redirect_location = redirect_response.headers['location']

# Extract the client_id query parameter from the redirect.
parsed = six.moves.urllib.parse.urlparse(redirect_location)
query_string = six.moves.urllib.parse.parse_qs(parsed.query)
# Print JSON output to stdout
jsondata = {
    "client_id": (query_string['client_id'][0])
    }
sys.stdout.write(json.dumps(jsondata))
