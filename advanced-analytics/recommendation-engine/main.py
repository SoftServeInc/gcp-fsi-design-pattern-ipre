""" Investment products recommendation engine service. 

The IPRE service takes two arguments:
    1/ uuid (required, str) -- unique user ID from the valid UUID list.
    2/ riskAversion (optional, float) -- risk-aversion factor in a range from 0.0 to 1.0.

The IPRE service returns recommendation of investment products with portfolio analytics
in a form of JSON. """

import os

from flask import Flask, request

import recommendation_engine
import statistics

__valid_uuids__ = [
    "user-0000000000000001",
    "user-0000000000000501",
    "user-0000000000000999"
]

app = Flask(__name__)


@app.route('/', methods=['GET'])
def re_engine():
    uuid = request.args.get('uuid')
    riskAversion = request.args.get('riskAversion', None, type=float)
    if not uuid:
        return 'UUID is not specified', 400
    if uuid not in __valid_uuids__:
        return 'Received unexpected UUID', 400
    if riskAversion and (riskAversion < 0.0 or riskAversion > 1.0):
        return 'Received invalid risk aversion', 400
    result = recommendation_engine.make_recommendation(
        uuid=uuid,
        riskAversion=riskAversion,
    )
    return result


@app.route('/stat/', methods=['GET'])
def basic_stat():
    asset_name = request.args.get('asset_name')
    if not asset_name:
        return 'Asset name is not specified', 400
    return statistics.basic(asset_name)


@app.route('/stat/detailed/', methods=['GET'])
def detailed_stat():
    asset_name = request.args.get('asset_name')
    if not asset_name:
        return 'Asset name is not specified', 400
    return statistics.detailed(asset_name)


@app.route('/stat/history/', methods=['GET'])
def history():
    asset_name = request.args.get('asset_name')
    if not asset_name:
        return 'Asset name is not specified', 400
    return statistics.history(asset_name)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
