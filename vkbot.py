# -*- coding: utf-8 -*-
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from botconfig import *
import random
import json
from edit_json import *
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def plus_count(from_id, teams_pass):
    '''
    Добавление 1 балла к команде
    '''

    load_data = json_read(load_data_file)

    for team in teams_pass:
        if team['team_id'] == from_id:
            load_data[f"team{teams_pass.index(team) + 1}"] += 1

    write_json(load_data_file, load_data)


def minus_count(from_id, teams_pass):
    '''
    Удаление 1 балла у команды
    '''

    load_data = json_read(load_data_file)

    for team in teams_pass:
        if team['team_id'] == from_id:
            if load_data[f"team{teams_pass.index(team) + 1}"] > 0:
                load_data[f"team{teams_pass.index(team) + 1}"] -= 1
                write_json(load_data_file, load_data)


write_json(keyboard_position_file, {})

game_end = False

# масив с JSON списками хранящими ключ пользователя и его id(команды)
teams_pass = [{"team_pass": None, "team_id": None, "done": "false"},
              {"team_pass": None, "team_id": None, "done": "false"},
              {"team_pass": None, "team_id": None, "done": "false"}]


def end_game(registred_id, vk):
    global game_end
    global teams_pass
    game_end = True

    # читаем JSON файл с вопросами
    json_file_data = json_read(database_file_name)

    # удаляем костыли из базы данных (не работает но фиксить некогда :( )
    for task_list in json_file_data:
        if task_list["task"] == "crutch":
            del json_file_data[json_file_data.index(task_list)]
            print(json_file_data)
    write_json(database_file_name, json_file_data)

    # инфа о тимах
    teams_info = json_read(load_data_file)

    mas = []

    mas.append(teams_info["team1"])
    mas.append(teams_info["team2"])
    mas.append(teams_info["team3"])

    max_count = max(mas)

    win_team_index = mas.index(max_count)

    win_team_id = teams_pass[win_team_index]["team_id"]

    for user in registred_id:
        vk.messages.send(
            peer_id=int(user),
            random_id=get_random_id(),
            message=f"Победитель: https://vk.com/id{win_team_id}"
        )
    vk.messages.send(
        peer_id=admin_id,
        random_id=get_random_id(),
        message=f"Победитель: https://vk.com/id{win_team_id}"
    )

    load_data = json_read(load_data_file)
    load_data['winner'] = f"https://vk.com/id{win_team_id}"
    write_json(load_data_file, load_data)


def main():
    global game_end
    global teams_pass

    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()

    longpoll = VkBotLongPoll(vk_session, group_id)

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

    load_data = {
        "team1": 0,
        "team2": 0,
        "team3": 0,
        "winner": ""
    }

    write_json(load_data_file, load_data)

    for event in longpoll.listen():

        # # условие которое не выполняется
        # if teams_pass[0]["done"] == True and teams_pass[1]["done"] == True and teams_pass[2]["done"] == True:
        #     print('Все команды выполнили задания !')

        # если пришло новое сообщение
        if event.type == VkBotEventType.MESSAGE_NEW:
            if game_end == False:
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

                        # создаём костыль
                        data = {
                            "task": "crutch",
                            "options": ["crutch0", "crutch1", "crutch2", "crutch3", "crutch4"],
                            "true_option": 0,
                            "resolved": "false"
                        }

                        # читаем JSON файл
                        json_file_data = json_read(database_file_name)

                        # добавляем в результат data костыль
                        json_file_data.append(data)

                        # записываем обратно в файл наш костыль
                        func_return = write_json(database_file_name, json_file_data)


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
                                                                          "team_id": event.obj.from_id, 'done': 'false'}
                                    # добавляем ключ в использованные
                                    expired_keys.append(event.obj.text)

                                    # добавляем команду (id пользователя) в зарегестрированынх
                                    registred_id.append(event.obj.from_id)

                                    # индекс команды в teams_pass
                                    team_count = teams_pass.index(
                                        {'team_pass': event.obj.text, 'team_id': event.obj.from_id, 'done': 'false'})

                                    # отправляем сообщение об успешной регистрации
                                    vk.messages.send(
                                        peer_id=event.obj.from_id,
                                        random_id=get_random_id(),
                                        message=f"Ключ принят ! Вы зарегестрированы как команда #{int(team_count) + 1}"
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
                if len(registred_id) == 3 and event.obj.from_id != admin_id:

                    # читаем JSON файл с поизициями клавиатуры
                    json_file_data = json_read(keyboard_position_file)

                    # если получаем пустой масив
                    if not json_file_data:

                        first_task = json_read(database_file_name)[0]

                        keyboard = VkKeyboard(one_time=True)

                        down_option = first_task["options"][-1]
                        for option in first_task["options"]:
                            keyboard.add_button(option, color=VkKeyboardColor.DEFAULT)
                            if not option == down_option:
                                keyboard.add_line()  # Переход на вторую строку

                        for team_id in registred_id:
                            vk.messages.send(
                                peer_id=team_id,
                                random_id=get_random_id(),
                                keyboard=keyboard.get_keyboard(),
                                message=start_user_game_msg

                            )

                            vk.messages.send(
                                peer_id=team_id,
                                random_id=get_random_id(),
                                message=first_task["task"]

                            )

                        my_str = '{'
                        punct = ''
                        for id in registred_id:
                            if id != registred_id[-1]:
                                punct = ','
                            else:
                                punct = ''
                            my_str += f'"{id}":0{punct}'
                        my_str += "}"

                        data = json.loads(str(my_str))
                        print(data)
                        func_return = write_json(keyboard_position_file, data)
                        print(func_return)

                    else:
                        json_keyboard_file_data = json_read(keyboard_position_file)
                        json_file_data = json_read(database_file_name)
                        print(json_keyboard_file_data)
                        print()
                        user_keyboard_position = json_keyboard_file_data[str(event.obj.from_id)]

                        try:
                            options_index = json_file_data[user_keyboard_position]["options"].index(event.obj.text)
                        except:
                            options_index = "ERROR"

                        if options_index != "ERROR":
                            if options_index == json_file_data[user_keyboard_position]["true_option"]:

                                # отмечаем вопрос как решёный (могло быть фичей но дедлайн 6ого марта :( )
                                # json_file_data[json_keyboard_file_data[str(event.obj.from_id)]]["resolved"] = "true"
                                # write_json(database_file_name, json_file_data)

                                # переходим на следующию позицию клавиатуры
                                json_keyboard_file_data[str(event.obj.from_id)] += 1
                                write_json(keyboard_position_file, json_keyboard_file_data)

                                # определяем последний вариант ответа
                                down_option = \
                                    json_file_data[json_keyboard_file_data[str(event.obj.from_id)]]["options"][-1]

                                # добавляем 1 балл команде
                                plus_count(event.obj.from_id, teams_pass)

                                # отправляем сообщение о том что ответ верный
                                vk.messages.send(
                                    peer_id=event.obj.from_id,
                                    random_id=get_random_id(),
                                    message="Ответ верный: +1"
                                )

                                # получаем последние задание в базе (то есть костыль)
                                down_task = json_file_data[-1]["task"]

                                # если это не последние задание (костыль в базе)
                                if down_task != json_file_data[json_keyboard_file_data[str(event.obj.from_id)]]["task"]:

                                    # генерируем клавиатуру
                                    keyboard = VkKeyboard(one_time=True)
                                    for option in json_file_data[json_keyboard_file_data[str(event.obj.from_id)]][
                                        "options"]:
                                        keyboard.add_button(option, color=VkKeyboardColor.DEFAULT)
                                        if not option == down_option:
                                            keyboard.add_line()  # Переход на вторую строку

                                    # отправляем следующий вопрос с клавиатурой
                                    vk.messages.send(
                                        peer_id=event.obj.from_id,
                                        random_id=get_random_id(),
                                        keyboard=keyboard.get_keyboard(),
                                        message=json_file_data[json_keyboard_file_data[str(event.obj.from_id)]]["task"]
                                    )

                                else:
                                    # записываем в teams_pass информацию о том что команда решила все задания
                                    for team in teams_pass:
                                        if team['team_id'] == event.obj.from_id:
                                            team["done"] = True

                                    vk.messages.send(
                                        peer_id=event.obj.from_id,
                                        random_id=get_random_id(),
                                        message="Вы закончили выполнение заданий !"
                                    )

                                    if teams_pass[0]["done"] == True and teams_pass[1]["done"] == True and \
                                            teams_pass[2][
                                                "done"] == True:
                                        print('Все команды выполнили задания !')
                                        end_game(registred_id, vk)

                            # иначе то есть если ответ не верный
                            else:

                                # переходим на следующию позицию клавиатуры
                                json_keyboard_file_data[str(event.obj.from_id)] += 1
                                write_json(keyboard_position_file, json_keyboard_file_data)

                                # определяем последний вариант ответа
                                down_option = \
                                    json_file_data[json_keyboard_file_data[str(event.obj.from_id)]]["options"][-1]

                                # добавляем 1 балл команде
                                minus_count(event.obj.from_id, teams_pass)

                                # отправляем сообщение о том что ответ верный
                                vk.messages.send(
                                    peer_id=event.obj.from_id,
                                    random_id=get_random_id(),
                                    message="Ответ неверный: -1"
                                )

                                # получаем последние задание в базе (то есть костыль)
                                down_task = json_file_data[-1]["task"]

                                # если это не последние задание (костыль в базе)
                                if down_task != json_file_data[json_keyboard_file_data[str(event.obj.from_id)]]["task"]:

                                    # генерируем клавиатуру
                                    keyboard = VkKeyboard(one_time=True)
                                    for option in json_file_data[json_keyboard_file_data[str(event.obj.from_id)]][
                                        "options"]:
                                        keyboard.add_button(option, color=VkKeyboardColor.DEFAULT)
                                        if not option == down_option:
                                            keyboard.add_line()  # Переход на вторую строку

                                    # отправляем следующий вопрос с клавиатурой
                                    vk.messages.send(
                                        peer_id=event.obj.from_id,
                                        random_id=get_random_id(),
                                        keyboard=keyboard.get_keyboard(),
                                        message=json_file_data[json_keyboard_file_data[str(event.obj.from_id)]]["task"]
                                    )

                                else:
                                    # записываем в teams_pass информацию о том что команда решила все задания
                                    for team in teams_pass:
                                        if team['team_id'] == event.obj.from_id:
                                            team["done"] = True

                                    vk.messages.send(
                                        peer_id=event.obj.from_id,
                                        random_id=get_random_id(),
                                        message="Вы закончили выполнение заданий !"
                                    )

                                    if teams_pass[0]["done"] == True and teams_pass[1]["done"] == True and \
                                            teams_pass[2]["done"] == True:
                                        print('Все команды выполнили задания !')
                                        end_game(registred_id, vk)



                        else:
                            vk.messages.send(
                                peer_id=event.obj.from_id,
                                random_id=get_random_id(),
                                message="Вы можете использовать только ответы на "
                                        "вопросы либо вы уже закончили викторину"
                            )
            else:
                vk.messages.send(
                    peer_id=event.obj.from_id,
                    random_id=get_random_id(),
                    message="Игра окончена !"
                )
        print(teams_pass)


if __name__ == '__main__':
    main()
