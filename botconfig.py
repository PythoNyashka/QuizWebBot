from my_personal_data import *

# string
token = my_personal_token

# string
group_id = my_personal_group_id

# string
admin_id = my_personal_admin_id

# database_completed = False

database_file_name = "database.json"

keyboard_position_file = "keyboard_position.json"

load_data_file = "load.json"

team_info_file = "team_info.json"

database_msg_text = "database_completed = False \n" \
                    "- - - - - - - - - - - \n" \
                    "Для добавления записи в базу данных отправьте: \n" \
                    "!add Вопрос:Ответ1|Ответ2|Ответ3|Ответ4|Ответ5>Номер верного ответа \n" \
                    "- - - - - - - - - - - \n" \
                    "Пример: \n" \
                    "!add Какого цвета Влад ?:Жёлтого|Синего|Голубого|Фиолетового|Оранжевого>2 \n" \
                    "- - - - - - - - - - - \n" \
                    "Не используйте разделительные символы ':'  '|' '>' в тексте ! Это может вызвать непредвиденные ошибки ! \n" \
                    "- - - - - - - - - - - \n" \
                    "Для чтения базы данных использует '!readdb' \n" \
                    "Для удаления вопроса из базы данных используйте '!deltask [индек элемента]' \n" \
                    "- - - - - - - - - - - \n" \
                    "Если вы уверены что база данных заполнена отправьте '!startgame' что бы начать викторину \n"

syntax_error = "Произошла непредвиденная ошибка, попробуйте проверить синтаксис"

database_is_empty = "В базе данных ещё нет вопросов"

start_game_msg = "ВНИМАНИЕ: database_completed = True \n" \
                 "Для генерации ключей команд отправьте любое сообщение !"

start_user_game_msg = f"Все 3 команды зарегестрированы ! \n" \
    f"Викторина запущена ! \n" \
    f"Вам будет отправлен первый вопрос ..."
