import random
from collections import defaultdict
import statistics

from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


def build_api_query(date: date, tile_ids: list) -> str:
    api_request = (
        BASE_URL
        + "/heatmaps/dwell-density/daily/{0}".format(date.isoformat())
        + "?tiles="
        + "&tiles=".join(map(str, tile_ids))
    )
    return api_request

def compute_density_baseline(tile_ids: list):
    # The baseline is the median value, for the corresponding day of the week,
    # during the nb_days following start_date"
    start_date = date(year=2020, month=1, day=6)
    nb_days = 29
    day2densities = defaultdict(lambda: [])
    for delta in range(nb_days):
        dt = start_date + timedelta(days=delta)
        day2densities[dt.weekday()].append(get_daily_density(dt, tile_ids))
    weekday2density = {wday: statistics.median(v)
                       for wday, v in day2densities.items()}
    return weekday2density


def get_daily_density(date: date, tile_ids: list) -> float:
    tiles_date = oauth.get(build_api_query(date, tile_ids),
                           headers=headers).json()['tiles']
    return sum([t['score'] for t in tiles_date])


def get_density_variation(date: date, tile_ids: list, weekday2density: dict) -> float:
    daily_score_date = get_daily_density(date, tile_ids)
    density_baseline = weekday2density[date.weekday()]
    variation = (daily_score_date - density_baseline) / density_baseline
    return 100*variation


def get_tile_ids_postal_code(postal_code: int) -> list:
    # Randomly sample MAX_NB_TILES_REQUEST tile ids
    # associated with the postal code of interest
    muni_tiles_json = oauth.get(
        BASE_URL + "/grids/postal-code-areas/{0}".format(postal_code), headers=headers).json()
    tile_ids = random.sample([t["tileId"]
                              for t in muni_tiles_json["tiles"]], MAX_NB_TILES_REQUEST)
    return tile_ids


def get_density_variation_time_period(tile_ids, start_date, nb_days):
    weekday2density = compute_density_baseline(tile_ids)
    date2variation = dict()
    for delta in range(nb_days):
        dt = start_date + timedelta(days=delta)
        date2variation[dt] = get_density_variation(
            dt, tile_ids, weekday2density)
    return date2variation


def plot_density_variation_tile_ids(tile_ids, start_date, nb_days):
    date2variation = get_density_variation_time_period(
        tile_ids, start_date, nb_days)
    dates, scores = zip(*sorted(date2variation.items()))
    fig, ax = plt.subplots()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.grid()
    plt.ylim(-100, 100)
    plt.fill_between(dates, scores, alpha=0.5,
                     joinstyle="round", color='tab:blue')
    fig.autofmt_xdate(rotation=45)
    plt.ylabel("Percentage variation")
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    # The following base url is associated with the standard plan
    # For the demo plan, you need replace the word `standard` 
	# by `demo` in the URL
    BASE_URL = "https://api.swisscom.com/layer/heatmaps/standard"
    TOKEN_URL = "https://consent.swisscom.com/o/oauth2/token"
    MAX_NB_TILES_REQUEST = 100
    headers = {"scs-version": "2"}  # API version
    # customer key in the Swisscom digital market place
    client_id = ""
    # customer secret in the Swisscom digital market place
    client_secret = ""

    # Fetch an access token
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    oauth.fetch_token(token_url=TOKEN_URL, client_id=client_id,
                      client_secret=client_secret)
    postal_code = 1215
    plot_density_variation_tile_ids(get_tile_ids_postal_code(
        postal_code), start_date=date(year=2020, month=2, day=1), nb_days=270)
