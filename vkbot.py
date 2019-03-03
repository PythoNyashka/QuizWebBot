# -*- coding: utf-8 -*-
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from botconfig import *
import random
import json
from edit_json import *


def main():
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()

    longpoll = VkBotLongPoll(vk_session, group_id)

    # масив с JSON списками хранящими ключ пользователя и его id(команды)
    teams_pass = [{"team_pass": None, "team_id": None}, {"team_pass": None, "team_id": None},
                  {"team_pass": None, "team_id": None}]

    # масив с ключами пользователей(команд)
    user_pass_mas = []

    # масив с использоваными ключами
    expired_keys = []

    # масив с зарегестрированами пользователями (командами)
    registred_id = []

    # переменная хранящия True если игра начата и False если нет
    # по умолчанию False
    game_started = False

    database_completed = False

    for event in longpoll.listen():

        # если пришло новое сообщение
        if event.type == VkBotEventType.MESSAGE_NEW:

            # если сообщение от администратора
            if event.obj.from_id == admin_id:
                if database_completed:
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

                # если в начале строки сообщения '!add'
                elif event.obj.text.split()[0].strip() == '!add' and not database_completed:

                    # пытаемся составить JSON список для базы данных из сообщения и записать в файл
                    try:

                        msg = event.obj.text
                        msg = msg.replace('!add ', '')
                        task = msg.split(":")[0]
                        true_option = int(msg.split(":")[1].split(">")[-1])
                        options = msg.replace(f">{str(true_option)}", '').replace(f"{task}:", '')
                        options_mas = []

                        for option in options.split("|"):
                            options_mas.append(option)

                        data = {
                            "task": task,
                            "options": options_mas,
                            "true_option": true_option,
                            "resolved": "false"
                        }

                        # читаем JSON файл
                        json_file_data = json_read(database_file_name)

                        # добавляем в результат data
                        json_file_data.append(data)

                        # записываем обратно в файл
                        func_return = write_json(database_file_name, json_file_data)

                        vk.messages.send(
                            peer_id=admin_id,
                            random_id=get_random_id(),
                            message=f"Функция записи в JSON файл вернула: {func_return}"
                        )

                    # если что то пошло не так отправляем сообщение об ошибке синтаксиса
                    except:
                        vk.messages.send(
                            peer_id=admin_id,
                            random_id=get_random_id(),
                            message=syntax_error
                        )

                elif event.obj.text.split()[0].strip() == '!startgame':
                    database_completed = True
                    vk.messages.send(
                        peer_id=admin_id,
                        random_id=get_random_id(),
                        message=start_game_msg
                    )

                # если в начале строки сообщения '!readdb'
                elif event.obj.text.split()[0].strip() == '!readdb' and not database_completed:

                    # читаем JSON файл с вопросами не пустой
                    json_file_data = json_read(database_file_name)

                    # если JSON файл с вопросами не пустой
                    if json_file_data:

                        # массив с отформатированым текстом JSON файла для отправки в сообщении
                        all_data_text = []

                        for task in json_file_data:
                            data_text = f"Count: {json_file_data.index(task)} \n" \
                                f"task: {task['task']} \n" \
                                f"options: {task['options']} \n" \
                                f"true_option: {task['true_option']} \n" \
                                f"-------------------"

                            all_data_text.append(data_text)

                        # отправляем сообщение о том что база данных пуста
                        vk.messages.send(
                            peer_id=admin_id,
                            random_id=get_random_id(),
                            message="\n".join(all_data_text)
                        )

                    else:

                        # отправляем сообщение о том что база данных пуста
                        vk.messages.send(
                            peer_id=admin_id,
                            random_id=get_random_id(),
                            message=database_is_empty
                        )

                        # отправляем сообщение о том как можно добавить вопрос в базу данных
                        vk.messages.send(
                            peer_id=admin_id,
                            random_id=get_random_id(),
                            message=database_msg_text
                        )

                # если в начале строки сообщения '!deltask'
                elif event.obj.text.split()[0].strip() == '!deltask' and not database_completed:

                    # разделяем строку сообщения
                    del_pram = event.obj.text.split()

                    # пытаемся первое значение масива del_pram преобразовать в int
                    try:
                        data_index = int(del_pram[1])
                    # если у нас это не получается присваимаем False
                    except:
                        data_index = "ERROR"

                    print(data_index)

                    # если data_index не False
                    if data_index != "ERROR":

                        # читаем JSON файл с вопросами
                        json_file_data = json_read(database_file_name)
                        # удаляем елемент по его индеку
                        try:
                            del json_file_data[data_index]
                            del_json = "OK"
                        except:
                            del_json = "ERROR"

                        if del_json != "ERROR":
                            # результат записываем в JSON файл
                            func_return = write_json(database_file_name, json_file_data)
                        else:
                            func_return = "NONE"

                        vk.messages.send(
                            peer_id=admin_id,
                            random_id=get_random_id(),
                            message=f"Совершена попытка удалить элемент с индексом: {str(data_index)} \n"
                            f"Функция записи в JSON файл вернула: {func_return} \n"
                            f"Удаление записи в JSON файле вернуло: {del_json}"
                        )

                    else:
                        vk.messages.send(
                            peer_id=admin_id,
                            random_id=get_random_id(),
                            message=syntax_error
                        )

                # отправляем сообщение о том как можно заполнить базу данных
                else:
                    vk.messages.send(
                        peer_id=admin_id,
                        random_id=get_random_id(),
                        message=database_msg_text
                    )

            # если текст сообщения есть в масиве с ключами и id пользователя не id администратора
            # и database_completed = True
            if event.obj.text in user_pass_mas and event.obj.from_id != admin_id and database_completed:

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

            # если зарегестрировно 3 команды
            if len(registred_id) == 3:
                pass

            print(teams_pass)


if __name__ == '__main__':
    main()
