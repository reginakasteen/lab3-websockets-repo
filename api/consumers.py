import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from api.models import Profile

class OnlineUserConsumer(AsyncWebsocketConsumer):
    group_name = "online_users"

    async def connect(self):
        self.user = self.scope["user"]
        print("CONNECTED USER:", self.user, self.user.is_authenticated)

        if self.user.is_authenticated:
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            await self.set_online()
            await self.send_online_users_group()
        else:
            print("NOT AUTHENTICATED")
            await self.close()


    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.set_offline()
            await self.send_online_users_group()

            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        pass

    async def send_online_users_group(self):
        users = await self.get_online_users()
        message = {
            "type": "online_users",
            "data": users
        }
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "online_users_message",
                "message": message,
            }
        )

    async def online_users_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    @database_sync_to_async
    def set_online(self):
        profile = Profile.objects.get(user=self.user)
        profile.is_online = True
        profile.save()

    @database_sync_to_async
    def set_offline(self):
        profile = Profile.objects.get(user=self.user)
        profile.is_online = False
        profile.save()

    @database_sync_to_async
    def get_online_users(self):
        return list(Profile.objects.filter(is_online=True)
                    .values('user__username', 'name', 'is_online'))


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_name = f"{self.scope['url_route']['kwargs']['sender_id']}_{self.scope['url_route']['kwargs']['receiver_id']}"
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.save_message(data)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": data
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "message": event["message"]
        }))

    @database_sync_to_async
    def save_message(self, data):
        from api.models import Message, Profile, User
        sender = User.objects.get(id=data["sender"])
        receiver = User.objects.get(id=data["receiver"])
        return Message.objects.create(
            sender=sender,
            receiver=receiver,
            message=data["message"]
        )
