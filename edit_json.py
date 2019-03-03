
import json

def json_read(file_name):
    """
        Чтение JSON файла
    """
    try:
        json_data = json.load(open(file_name, 'r', encoding="utf8"))
    except:
        json_data = []
    return json_data


def write_json(file_name, data):
    """
        Запись в JSON файл
    """
    try:
        with open(file_name, 'w', encoding="utf8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        return "OK"
    except:
        return "ERROR"