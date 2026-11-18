import argparse
import json
import logging
import uuid

import httpx2


class RasaClient:
    def __init__(self, host="localhost", port="5008", endpoint="smart_suggest"):
        self.host = host
        self.port = port
        self.uuid = uuid.uuid1()
        self.rasa_endpoint = f"webhooks/{endpoint}/webhook"
        self.rasa_timeout = 30
        self.logger = logging.getLogger(__name__)

    def get_state(self):
        # curl localhost:5007/conversations/30bc4818-bac3-11f1-9b5a-9119d95f9945/tracker
        requestEndpoint = (
            "http://"
            + self.host
            + ":"
            + self.port
            + "/conversations/"
            + str(self.uuid)
            + "/tracker"
        )
        response = httpx2.get(requestEndpoint, timeout=self.rasa_timeout)
        return response.json()

    def tell_rasa(self, msg):
        """Sends a text message to rasa and gets the response.

        Sends an HTTP GET request to Rasa and waits asynchronously for the response.
        The response is a json string and contains various responses, having
        a ``text`` field, which is what this function returns. In case of empty text
        fields, an error message is returned to the client.

        Args:
            msg (str) : the text message of the user
        Returns:
            (str) : rasa's response to the user
        """

        try:
            all_responses = ""

            self.logger.debug(
                str(self.uuid) + " says '" + msg + "'. Forwarding to Rasa."
            )

            requestEndpoint = (
                "http://" + self.host + ":" + self.port + "/" + self.rasa_endpoint
            )

            requestBody = {"message": msg, "sender": str(self.uuid)}
            requestBody_json = json.loads(json.dumps(requestBody))
            # adding exceptions for bad statuses
            # from https://stackoverflow.com/a/16511493
            responseString = httpx2.post(url=requestEndpoint, json=requestBody_json)
            responseString.raise_for_status()
            appended_responses = [x["text"] for x in responseString.json()]
            all_responses = "".join(appended_responses)

            if all_responses is None:
                self.logger.error("Got None message from rasa. This should not happen.")
                self.logger.error("ERROR_RASA")
                all_responses = (
                    "An error has occured, please close and open the application."
                )
                raise ValueError("Received None message from Rasa")
            elif all_responses == "":
                self.logger.error("Rasa replied an empty string")
                all_responses = "I'm sorry, something went wrong, try again!"
                raise ValueError("Received empty message from Rasa")
            else:
                self.logger.debug("Got message from Rasa '" + all_responses + "'")

        except httpx2.RequestError as e:
            # HTTPError is raised for non-200 responses; the response
            # can be found in e.response.

            self.logger.error(str(e))
            all_responses = (
                "The chatbot couldnt be reached, are you sure it is running?"
            )

        return all_responses

    def do_conversation(self):
        print("Starting conversation, say something to your rasa chatbot")
        user_msg = ""
        while True:
            user_msg = input()
            res = self.tell_rasa(user_msg)
            print(res)

    def converse(self, input: str):
        return self.tell_rasa(input)


def parse_args():
    parser = argparse.ArgumentParser(
        prog="Rasa Tiny Client",
        description="Tiny client to test Rasa",
    )
    parser.add_argument("-e", "--endpoint", default="rest")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    tc = RasaClient(endpoint=args.endpoint)
    tc.do_conversation()
