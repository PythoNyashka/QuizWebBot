# -*- coding: utf-8 -*-
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from botconfig import *
import random


def main():
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()

    longpoll = VkBotLongPoll(vk_session, group_id)

    for event in longpoll.listen():

        # если пришло новое сообщение
        if event.type == VkBotEventType.MESSAGE_NEW:

            # Генерируем 3 сикретных ключа
            user_pass_mas = []
            for user_pass in range(3):
                pas = ""
                for x in range(8):  # Количество символов (16)
                    pas += random.choice(list(
                        '1234567890abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ'))  # Символы, из которых будет составлен пароль
                user_pass_mas.append(pas)

            # строка для отправки администратору содержащая ключи
            pass_string_msg = f"Первая команда: {user_pass_mas[0]} \n" \
                f"Вторая команда: {user_pass_mas[1]} \n" \
                f"Третья команда: {user_pass_mas[2]} \n"

            # отправляем сообщение с ключами администратору
            vk.messages.send(
                peer_id=admin_id,
                random_id=get_random_id(),
                message=pass_string_msg
            )

            print(event.obj.text)


if __name__ == '__main__':
    main()
