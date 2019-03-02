# -*- coding: utf-8 -*-
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from botconfig import *
import random
import json


def main():
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()

    longpoll = VkBotLongPoll(vk_session, group_id)

    teams_pass = [{"team_pass": None, "team_id": None}, {"team_pass": None, "team_id": None},
                  {"team_pass": None, "team_id": None}]

    user_pass_mas = []
    expired_keys = []
    registred_id = []

    for event in longpoll.listen():

        # если пришло новое сообщение
        if event.type == VkBotEventType.MESSAGE_NEW:

            # если сообщение от администратора
            if event.obj.from_id == admin_id:

                # считаем значения None в teams_pass
                none_count = 0
                for team_pass in teams_pass:
                    if team_pass["team_pass"] == None and team_pass["team_id"] == None:
                        none_count += 1

                # если все команды без ключей и у нас меньше чем 3 ключа
                if none_count == 3 and len(user_pass_mas) < 3:
                    # Генерируем 3 сикретных ключа
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

            # если текст сообщения есть в масиве с ключами и id пользователя не id администратора
            if event.obj.text in user_pass_mas and event.obj.from_id != admin_id:

                for team in teams_pass:
                    # если команды нет в массиве зарегестрированных команд
                    if not event.obj.from_id in registred_id:
                        # если ключ не был ранее использован
                        if not event.obj.text in expired_keys:
                            # если team_pass и team_id пусты
                            if team["team_pass"] == None and team["team_id"] == None:
                                # добовляем ключ и команду (id пользователя) в teams_pass
                                teams_pass[teams_pass.index(team)] = {"team_pass": event.obj.text,
                                                                      "team_id": event.obj.from_id}
                                # добавляем ключ в использованные
                                expired_keys.append(event.obj.text)

                                # добавляем команду (id пользователя) в зарегестрированынх
                                registred_id.append(event.obj.from_id)

                                # отправляем сообщение об успешной регистрации
                                vk.messages.send(
                                    peer_id=event.obj.from_id,
                                    random_id=get_random_id(),
                                    message=f"Ключ принят ! Вы зарегестрированы как команда #{teams_pass.index(team)}"
                                )
                                break
                        else:
                            vk.messages.send(
                                peer_id=event.obj.from_id,
                                random_id=get_random_id(),
                                message="Ключ уже использован другой командой !"
                            )
                            break
                    else:
                        vk.messages.send(
                            peer_id=event.obj.from_id,
                            random_id=get_random_id(),
                            message="Выша команда уже зарегестрирована !"
                        )
                        break

            print(teams_pass)


if __name__ == '__main__':
    main()
