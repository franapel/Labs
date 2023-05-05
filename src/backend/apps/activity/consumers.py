import json
from channels.generic.websocket import WebsocketConsumer
from .utils import decryptAES, validateWorkstationByRegex, getCurrentTimestamp
from asgiref.sync import async_to_sync
from apps.activity.models import Session


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        enc = self.scope["url_route"]["kwargs"]["enc"]
        dec = decryptAES(enc, "gUkXp2s5v8y/B?E(G+KbPeShVmYq3t6w")
        if (dec == "iamadmin"):
            self.room_group_name = "labs"
            async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)            
            self.accept()
        elif (validateWorkstationByRegex(dec)):
            self.room_group_name = "labs"
            self.workstation = dec
            async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
            self.accept()
        else:            
            self.close()        

    def disconnect(self, _):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "workstation.disconnect",
                "workstation": self.workstation
            },
        )
        async_to_sync(self.channel_layer.group_discard)("labs", self.channel_name)


    def receive(self, text_data):
        data = json.loads(text_data)
        if data["type"] == "alive":
            session = Session.objects.filter(workstation__name=self.workstation).order_by("start").last()
            if session.end is None:
                session.alive = getCurrentTimestamp()
                session.save()
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "workstation.alive",
                    "workstation": self.workstation
                },
            )
        

    def workstation_alive(self, event):
        self.send(text_data=json.dumps({
            "workstation": event["workstation"],
            "type": "alive"
        }))

    def workstation_disconnect(self, event):
        self.send(text_data=json.dumps({
            "workstation": event["workstation"],
            "type": "disconnect"
        }))