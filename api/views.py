from api import api
from flask import jsonify


@api.route("/", methods=["GET"])
def base_url():
    """Base url to test API."""

    response = {"response": "Hello world!"}

    return jsonify(response)
