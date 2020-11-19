# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import MessageFactory, TurnContext
from botbuilder.core.teams import TeamsActivityHandler
from botbuilder.schema import Mention


class MentionBot(TeamsActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        await turn_context.send_activity(MessageFactory.text("asdfqwery"))
