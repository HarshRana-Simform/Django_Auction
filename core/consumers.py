import json
from channels.generic.websocket import AsyncWebsocketConsumer


class AuctionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join the group for all auction updates
        self.group_name = 'auction_dashboard'
        print(f"Connecting to group {self.group_name}")
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Receive message from the group for the bid update
    async def send_auction_update(self, event):
        await self.send(text_data=json.dumps({
            'item_id': event['item_id'],
            'current_bid': event['current_bid'],
        }))

    # Receive message from the group for the auction status update and for reloading
    async def send_status_update(self, event):
        await self.send(text_data=json.dumps({
            'item_id': event['item_id'],
            'status': event['status'],
        }))
