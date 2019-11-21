# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import sys
from datetime import datetime
from types import MethodType

from quart import Quart, request, Response
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    TurnContext,
    BotFrameworkAdapter,
    MemoryStorage
)
from botbuilder.schema import Activity, ActivityTypes
from activity_log import ActivityLog
from bots import MessageReactionBot
# from threading_helper import run_coroutine

# Create the Flask app
APP = Quart(__name__, instance_relative_config=True)
APP.config.from_object("config.DefaultConfig")

# Create adapter.
# See https://aka.ms/about-bot-adapter to learn more about how bots work.
SETTINGS = BotFrameworkAdapterSettings(APP.config["APP_ID"], APP.config["APP_PASSWORD"])
ADAPTER = BotFrameworkAdapter(SETTINGS)


# Catch-all for errors.
async def on_error( # pylint: disable=unused-argument
    self, context: TurnContext, error: Exception
):
    # This check writes out errors to console log .vs. app insights.
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")
    await context.send_activity(
        "To continue to run this bot, please fix the bot source code."
    )
    # Send a trace activity if we're talking to the Bot Framework Emulator
    if context.activity.channel_id == "emulator":
        # Create a trace activity that contains the error object
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.utcnow(),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
        )
        # Send a trace activity, which will be displayed in Bot Framework Emulator
        await context.send_activity(trace_activity)


ADAPTER.on_turn_error = MethodType(on_error, ADAPTER)

MEMORY = MemoryStorage()
ACTIVITY_LOG = ActivityLog(MEMORY)
# Create the Bot
BOT = MessageReactionBot(ACTIVITY_LOG)

# Listen for incoming requests on /api/messages.s
@APP.route("/api/messages", methods=["POST"])
async def messages():
    # Main bot message handler.
    if "application/json" in request.headers["Content-Type"]:
        body = await request.json
    else:
        return Response("", status=415)

    activity = Activity().deserialize(body)
    auth_header = (
        request.headers["Authorization"] if "Authorization" in request.headers else ""
    )

    try:
        print("about to create task")
        print("about to run until complete")
        await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
        print("is now complete")
        return Response("", status=201)
    except Exception as exception:
        raise exception


if __name__ == "__main__":
    try:
        APP.run(debug=False, port=APP.config["PORT"])  # nosec debug
    except Exception as exception:
        raise exception
