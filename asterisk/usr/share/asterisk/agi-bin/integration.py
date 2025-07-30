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
    caller = agi.env.get("agi_callerid")
    called = agi.env.get("agi_extension")

    # answer call and log relevant information
    agi.answer()
    agi.verbose(f"{caller}/{called} registering")

    # play registration message
    agi.stream_file("selfservice_ansage")

    try:
        # post to api
        response = requests.post(
            f"http://{uuru_host}/api/v1/provisioning/dect",
            json={caller: caller, called: called},
        )

        # check response
        if not response.status_code == 200:
            raise Exception(f"api returned {response.status_code}")

        agi.verbose(f"{caller}/{called} success")

    except Exception as e:
        # give user error message
        agi.verbose(f"{caller}/{called} error: {e}")
        agi.stream_file("selfservice_error")

    finally:
        agi.hangup()
