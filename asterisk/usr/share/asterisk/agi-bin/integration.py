#!/usr/bin/env python3

import asterisk.agi
import requests
import os

if __name__ == "__main__":
    # get uuru_host
    uuru_host = os.environ.get("UURU_WEB_HOST", "127.0.0.1:8000")

    # initialize AGI object
    agi = asterisk.agi.AGI()

    # get caller and called information
    tmp_extension = agi.env.get("agi_callerid")
    token = agi.env.get("agi_extension")

    # answer call and log relevant information
    agi.answer()
    agi.verbose(f"{tmp_extension}/{token} registering")

    # play registration message
    agi.stream_file("selfservice_ansage", escape_digits="6969")

    try:
        # post to api
        response = requests.post(
            f"http://{uuru_host}/telephoning/dect/",
            json={"tmp_extension": tmp_extension, "token": token},
        )

        # check response
        if not response.status_code == 200:
            raise Exception(f"api returned {response.status_code}")

        agi.verbose(f"{tmp_extension}/{token} success")

    except Exception as e:
        # give user error message
        agi.verbose(f"{tmp_extension}/{token} error: {e}")
        agi.stream_file("selfservice_error")

    finally:
        agi.hangup()
