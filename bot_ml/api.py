from flask import Flask, request, jsonify, render_template, send_from_directory
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import timedelta
import csv
import os
import os
import csv
import glob
import threading
from main import run_spider, job_function
from utils import get_project_root
from scrapy.utils.log import configure_logging
from apscheduler.schedulers.background import BackgroundScheduler 
from apscheduler.jobstores.base import JobLookupError
import logging

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)


app = Flask(__name__,  template_folder="templates")
app.secret_key = 'sua_chave_secreta_aqui'  

resource_path = os.path.join(get_project_root(), "resource")
resource_path_exel = os.path.join(get_project_root(), "exel")
cron_file = os.path.join(get_project_root(), "cron.csv")
user_file = os.path.join(get_project_root(), "user.csv")
scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")


app.permanent_session_lifetime = timedelta(hours=24)

job_id = "discos_job_id"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



def check_user(username, password):
    with open(user_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == username and row[1] == password:
                return True
    return False


class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if check_user(username, password):
            user = User(username)
            login_user(user)
            session.permanent = True  
            return redirect(url_for('home'))
        else:
            flash('Usuário ou senha incorretos!', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@login_required
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
    


@app.route('/set-cron', methods=['GET', 'POST'])
def set_cron():
    if request.method == 'GET':
        with open(cron_file, 'r', encoding='utf-8') as file:
            data = file.read().splitlines()
        return jsonify({"cron": data})

    if request.method == 'POST':
        data = request.json
        cron_time = data.get("time", None)

        if cron_time:
            print(f"[LOG] Novo cron recebido: {cron_time}")

            with open(cron_file, 'w', encoding='utf-8') as file:
                file.write(cron_time + "\n")

            try:
                hour, minute = cron_time.split(":")
                print(f"[LOG] Definindo cron para Hora: {hour}, Minuto: {minute}")
            except ValueError:
                return jsonify({"error": "Formato inválido. Use HH:MM ou *:MM"}), 400
            

            try:
                scheduler.remove_job(job_id)
            except JobLookupError:
                print(f"[LOG] Nenhum job encontrado com ID {job_id}, criando um novo.")

            if hour == "*":
                scheduler.add_job(job_function, 'interval', minutes=int(minute), timezone="America/Sao_Paulo", id=job_id, replace_existing=True)
            else:
                scheduler.add_job(job_function, 'cron', hour=int(hour), minute=int(minute), timezone="America/Sao_Paulo", id=job_id, replace_existing=True)
            print(f"Jobs ativos: {scheduler.get_jobs()}")
            return jsonify({"message": f"Cron configurado para {cron_time}"}), 201

    return jsonify({"message": "Falha na configuração do cron."}), 400



def initialize_cron():
    if not os.path.exists(cron_file):
        with open(cron_file, 'w', encoding='utf-8') as file:
            file.write('*:25\n')
    
    with open(cron_file, 'r', encoding='utf-8') as file:
        cron_time = file.read().strip()

    print(f"[LOG] Inicializando cron com valor: {cron_time}")

    if cron_time:
        try:
            scheduler.remove_job(job_id)
        except JobLookupError:
            print(f"[LOG] Nenhum job encontrado com ID {job_id}, criando um novo.")
        try:
            hour, minutes = cron_time.split(":")
            print(f"[LOG] Hora: {hour}, Minuto: {minutes}")
            if hour == "*":
                scheduler.add_job(job_function, 'interval', minutes=int(minutes), timezone="America/Sao_Paulo", id=job_id, replace_existing=True)
            else:
                scheduler.add_job(job_function, 'cron', hour=int(hour), minute=int(minutes), timezone="America/Sao_Paulo", id=job_id, replace_existing=True)
        except ValueError:
            print("[ERRO] Formato de cron inválido, ignorando...")
        print(f"Jobs ativos: {scheduler.get_jobs()}")



@app.route('/delete-file-xlsx', methods=['DELETE'])
def manage_delete_xlsx():
    data = request.json
    file_name = data.get("file_name")

    if not file_name:
        return jsonify({"error": "Nome do arquivo não fornecido"}), 400

    file_path = os.path.join(resource_path_exel, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({"message": f"Arquivo '{file_name}' deletado com sucesso"}), 200
    else:
        return jsonify({"error": f"Arquivo '{file_name}' não encontrado"}), 404



@app.route('/clear-cache', methods=['DELETE'])
def manage_delete_cache():
    file_cache_path = os.path.join(get_project_root(), "ja_coletados.csv")

    if not os.path.exists(file_cache_path):
        return jsonify({"error": "Arquivo 'ja_coletados.csv' não encontrado"}), 404

    try:
        open(file_cache_path, 'w').close()
        return jsonify({"message": "Cache limpo com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao limpar o cache: {str(e)}"}), 500



def start_scheduler():
    if not scheduler.running:
        scheduler.start()


if __name__ == '__main__':
    os.environ['TZ'] = 'America/Sao_Paulo'    
    configure_logging()
    initialize_cron()

    if not scheduler.running:
        scheduler.start()
    
    app.run(debug=True, host="0.0.0.0", port=5000)
