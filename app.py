from flask import Flask, render_template, json, request
from multiprocessing import Process, Value
import pickle

app = Flask(__name__)
i = 10


@app.route('/')
def index():
    return render_template('index.html')


def json_read(file_name):
    with open(file_name, 'r') as f:
        json_data = json.loads(f.read())
    return json_data


@app.route('/get_len', methods=['GET', 'POST'])
def get_len():
    data = json_read("load.json")
    print(data)
    return json.dumps(data)


if __name__ == '__main__':
    app.run(debug=True)
