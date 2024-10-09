from flask import Flask, request, jsonify
import os
import requests
import zipfile
import random
import string
import difflib

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

@app.route('/sum', methods=['POST'])
def sum_api():
    data = request.get_json()
    num_list = data.get('numbers', [])
    total_sum = sum(num_list)
    return jsonify({'sum': total_sum})

@app.route('/average', methods=['POST'])
def average_api():
    data = request.get_json()
    num_list = data.get('numbers', [])
    total_sum = sum(num_list)
    length = len(num_list)
    if length == 0:
        return jsonify({'average': 0})
    return jsonify({'average': total_sum / length})

@app.route('/mode', methods=['POST'])
def mode_api():
    data = request.get_json()
    num_list = data.get('numbers', [])
    freq_dict = {}
    for num in num_list:
        if num in freq_dict:
            freq_dict[num] += 1
        else:
            freq_dict[num] = 1
    max_freq = max(freq_dict.values())
    for num, freq in freq_dict.items():
        if freq == max_freq:
            return jsonify({'mode': num})
    return jsonify({'mode': None})



def generate_random_string(length=5):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

@app.route('/download_and_unzip', methods=['POST'])
def download_and_unzip_api():
    url = request.json.get('url')
    if not url:
        return jsonify({"status": "failure", "message": "缺少下载地址", "data": {}})
    response = requests.get(url)
    if response.status_code == 200:
        file_name = os.path.basename(url)
        with open(file_name, 'wb') as f:
            f.write(response.content)

        random_str = generate_random_string()
        unzip_folder_name = f'{os.path.splitext(file_name)[0]}_{random_str}'
        unzip_folder = os.path.join(os.getcwd(), unzip_folder_name)
        if not os.path.exists(unzip_folder):
            os.makedirs(unzip_folder)

        with zipfile.ZipFile(file_name, 'r') as zip_ref:
            zip_ref.extractall(unzip_folder)

        os.remove(file_name)
        full_path = os.path.abspath(unzip_folder)
        first_file_path = None
        for root, dirs, files in os.walk(unzip_folder):
            if files:
                first_file_path = os.path.join(root, files[0])
                break

        first_file_content = None
        if first_file_path:
            with open(first_file_path, 'r', encoding='utf-8') as f:
                first_file_content = f.read()

        return jsonify({"status": "success", "message": "", "data": {"unzippedFolderPath": full_path, "firstFilePath": first_file_path, "firstFileContent": first_file_content}})
    else:
        return jsonify({"status": "failure", "message": "下载失败", "data": {}})

def similarity(text1, text2):
    s = difflib.SequenceMatcher(None, text1, text2)
    return s.ratio()
		
@app.route('/compare_texts', methods=['POST'])
def compare_texts():
    data = request.get_json()
    texts_left_str = data.get('texts_left', '')
    texts_right_str = data.get('texts_right', '')
    texts_left = texts_left_str.split('\n') if texts_left_str else []
    texts_right = texts_right_str.split('\n') if texts_right_str else []
    if not texts_left or not texts_right:
        return jsonify({"status": "failure", "message": "两个参数都不能为空", "data": None})
    results = []
    for left_text, right_text in zip(texts_left, texts_right):
        sim = similarity(left_text, right_text)
        results.append({"text_left": left_text, "text_right": right_text, "similarity": sim})
    return jsonify({"status": "success", "message": "", "data": {"res": results}})
		

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=60002)