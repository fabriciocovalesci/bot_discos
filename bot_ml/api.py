from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import csv
import glob
from main import run_spider
from utils import get_project_root
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__,  template_folder="templates")
scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")
scheduler.start()

resource_path = os.path.join(get_project_root(), "resource")

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/run', methods=['POST'])
def run():
    data = request.json
    search_query = data.get("query")
    
    if not search_query:
        return jsonify({"error": "Query não fornecida"}), 400
    
    run_spider(search_query)
    return jsonify({"message": f"Busca iniciada para '{search_query}'"}), 200

@app.route('/input', methods=['GET', 'POST', 'DELETE'])
def manage_input():
    csv_file_path = os.path.join(resource_path, "input.csv")

    if request.method == 'GET':
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            data = [row[0] for row in reader]
        return jsonify({"input": data})

    data = request.json
    name = data.get("name")

    if request.method == 'POST':
        with open(csv_file_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([name])
        return jsonify({"message": f"'{name}' adicionado ao input.csv"}), 201

    if request.method == 'DELETE':
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        with open(csv_file_path, 'w', encoding='utf-8') as file:
            for line in lines:
                if line.strip("\n") != name:
                    file.write(line)

        return jsonify({"message": f"'{name}' removido do input.csv"}), 200
    

@app.route('/resultados', methods=['GET'])
def manage_resultados():
    folder_path = os.path.join(get_project_root(), "exel")
    xlsx_files = glob.glob(os.path.join(folder_path, "*.xlsx"))
    filenames = [os.path.basename(file) for file in xlsx_files]
    return jsonify({"resultados": filenames})


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    folder_path = os.path.join(get_project_root(), "exel")
    return send_from_directory(folder_path, filename, as_attachment=True)

    

@app.route('/proibidos', methods=['GET', 'POST', 'DELETE'])
def manage_proibidos():
    proibidos_file = os.path.join(get_project_root(), "proibidos.csv")

    if request.method == 'GET':
        with open(proibidos_file, 'r', encoding='utf-8') as file:
            data = file.read().splitlines()
        return jsonify({"proibidos": data})

    data = request.json
    name = data.get("name")

    if request.method == 'POST':
        with open(proibidos_file, 'a', encoding='utf-8') as file:
            file.write(name + "\n")
        return jsonify({"message": f"'{name}' adicionado aos proibidos"}), 201

    if request.method == 'DELETE':
        with open(proibidos_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        with open(proibidos_file, 'w', encoding='utf-8') as file:
            for line in lines:
                if line.strip("\n") != name:
                    file.write(line)

        return jsonify({"message": f"'{name}' removido dos proibidos"}), 200
    


@app.route('/set-cron', methods=['POST'])
def set_cron():
    data = request.json
    date = data.get('date')
    interval = data.get('interval')
    
    # Lógica para configurar o cron, por exemplo:
    # cron_expr = f"{minute} {hour} * * *"
    # Você pode configurar o cron com a data e o intervalo aqui
    
    return jsonify({"message": "Cron configurado com sucesso!"}), 200


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
