import random
import statistics
from collections import defaultdict

import matplotlib.pyplot as plt
from datetime import datetime, timedelta, date
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


def compute_density_baseline(tile_ids: list,
                             start_date=date(year=2020, month=1, day=6),
                             nb_days: int = 29) -> dict:
    # The baseline is the median value, for the corresponding day of the week,
    # during the nb_days following start_date"
    day2densities = defaultdict(list)
    for delta in range(nb_days):
        dt = start_date + timedelta(days=delta)
        day2densities[dt.weekday()].append(get_daily_density(dt, tile_ids))
    weekday2density = {wday: statistics.median(v)
                       for wday, v in day2densities.items()}
    return weekday2density


def get_daily_density(date: date, tile_ids: list) -> float:
    api_request = oauth.get(BASE_URL + "/heatmaps/dwell-density/daily/{0}".format(date.isoformat()),
                            headers=headers, params={'tiles': tile_ids})
    tiles_date = api_request.json()['tiles']
    return sum([t['score'] for t in tiles_date])


def get_density_variation(date: date, tile_ids: list, weekday2density: dict) -> float:
    daily_score_date = get_daily_density(date, tile_ids)
    density_baseline = weekday2density[date.weekday()]
    variation = (daily_score_date - density_baseline) / density_baseline
    return 100*variation


def get_tile_ids_postal_code(postal_code: int) -> list:
    # Randomly sample MAX_NB_TILES_REQUEST tile ids
    # associated with the postal code of interest
    tiles_json = oauth.get(
        BASE_URL + "/grids/postal-code-areas/{0}".format(postal_code), headers=headers).json()
    tile_ids = random.sample([t["tileId"]
                              for t in tiles_json["tiles"]], MAX_NB_TILES_REQUEST)
    return tile_ids


def get_density_variation_time_period(tile_ids, start_date, nb_days) -> dict:
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
    # by `demo` in the URL. Note that the demo plan data is limited 
    # to only 27/01/2020, which requires modifications to the code below.

    BASE_URL = "https://api.swisscom.com/layer/heatmaps/standard"
    TOKEN_URL = "https://consent.swisscom.com/o/oauth2/token"
    MAX_NB_TILES_REQUEST = 100
    headers = {"scs-version": "2"}  # API version
    client_id = "" # customer key in the Swisscom digital market place
    client_secret = "" # customer secret in the Swisscom digital market place

    assert client_id, "client id not defined"
    assert client_secret, "client_secret not defined"
    # Fetch an access token
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    oauth.fetch_token(token_url=TOKEN_URL, client_id=client_id,
                      client_secret=client_secret)
    postal_code = 1215
    plot_density_variation_tile_ids(get_tile_ids_postal_code(
        postal_code), start_date=date(year=2020, month=2, day=1), nb_days=120)
