# -*- coding: utf-8 -*-
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from botconfig import *


def main():
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()

    longpoll = VkBotLongPoll(vk_session, group_id)

    for event in longpoll.listen():

        # если пришло новое сообщение
        if event.type == VkBotEventType.MESSAGE_NEW:
            print(event.obj.text)


if __name__ == '__main__':
    main()