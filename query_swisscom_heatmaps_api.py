from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from datetime import datetime, timedelta
import pprint

BASE_URL = "https://api.swisscom.com/layer/heatmaps/demo"
TOKEN_URL = "https://consent.swisscom.com/o/oauth2/token"
MAX_NB_TILES_REQUEST = 100
headers = {"scs-version": "2"}  # API version

client_id = ""  # customer key in the Swisscom digital market place
client_secret = ""  # customer secret in the Swisscom digital market place

# Fetch an access token
client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)
oauth.fetch_token(token_url=TOKEN_URL, client_id=client_id,
                  client_secret=client_secret)

# Get all the first MAX_NB_TILES_REQUEST tile ids associated with the postal code of interest
postal_code = 1003
muni_tiles_json = oauth.get(
    BASE_URL + "/grids/postal-code-areas/{0}".format(postal_code), headers=headers
).json()
tile_ids = [t["tileId"] for t in muni_tiles_json["tiles"]][
    :MAX_NB_TILES_REQUEST
]

# define a start time and request the density for the following given number of hours
start_time = datetime(year=2020, month=1, day=27, hour=0, minute=0)
dates = [(start_time + timedelta(hours=delta)) for delta in range(24)]
date2score = dict()

for dt in dates:
    api_request = (
        BASE_URL
        + "/heatmaps/dwell-density/hourly/{0}".format(dt.isoformat())
        + "?tiles="
        + "&tiles=".join(map(str, tile_ids))
    )
    daily_total_density = sum(
        map(
            lambda t: t["score"],
            oauth.get(api_request, headers=headers).json()["tiles"],
        )
    )
    date2score[dt.isoformat()] = daily_total_density

# print the daily density for every date
print("The average hourly density for postal code {0}".format(postal_code))
pprint.PrettyPrinter(indent=4).pprint(date2score)
