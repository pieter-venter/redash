import logging
import requests

from redash.destinations import *
from redash.utils import json_dumps

# Implements a Hangouts Chat card as per the specification https://developers.google.com/hangouts/chat/
class HangoutsChat(BaseDestination):

    @classmethod
    def configuration_schema(cls):
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "title": "Webhook URL (get it from the room settings)"
                },
                "icon_url": {
                    "type": "string",
                    "title": "Icon URL (32x32 or multiple, png format)"
                }
            },
            "required": ["url"]
        }

    @classmethod
    def icon(cls):
        return 'fa-bolt'

    def dump(self, obj):
        for attr in dir(obj):
            if hasattr(obj, attr):
                logging.error("obj.%s = %s" % (attr, getattr(obj, attr)))

    def notify(self, alert, query, user, new_state, app, host, options):
        try:
            if new_state == "triggered":
                message = "<b><font color=\"#c0392b\">Triggered</font></b>"
            else:
                message = "<font color=\"#27ae60\">Went back to normal</font>"

            data = {
                "cards": [
                    {
                        "header": {
                            "title": alert.name
                        },
                        "sections": [
                            {
                                "widgets": [
                                    {
                                        "textParagraph": {
                                            "text": message
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }

            if options.get("icon_url"):
                data["cards"][0]["header"]["imageUrl"] = options.get("icon_url")

            # Hangouts Chat will create a blank card if an invalid URL (no hostname) is posted. Only add this if host was provided.
            if host:
                data["cards"][0]["sections"][0]["widgets"].append({
                    "buttons": [
                        {
                            "textButton": {
                                "text": "OPEN QUERY",
                                "onClick": {
                                    "openLink": {
                                        "url": "{host}/queries/{query_id}".format(host=host, query_id=query.id)
                                    }
                                }
                            }
                        }
                    ]
                })

            headers = {"Content-Type": "application/json; charset=UTF-8"}
            resp = requests.post(options.get("url"), data=json_dumps(data), headers=headers, timeout=5.0)
            if resp.status_code != 200:
                logging.error("webhook send ERROR. status_code => {status}".format(status=resp.status_code))
        except Exception:
            logging.exception("webhook send ERROR.")

register(HangoutsChat)