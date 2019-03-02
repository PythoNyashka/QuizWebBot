
import json

def json_read(file_name):
    """
        Чтение JSON файла
    """
    try:
        json_data = json.load(open(file_name, 'r', encoding="cp1251"))
    except:
        json_data = []
    return json_data


def write_json(file_name, data):
    """
        Запись в JSON файл
    """
    try:
        with open(file_name, 'w', encoding="cp1251") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        return "OK"
    except:
        return "ERROR"