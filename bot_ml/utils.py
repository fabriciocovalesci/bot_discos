

from decouple import config
import re
import os
import io
import sys
from datetime import date, datetime
import calendar
import json
import pathlib
from collections import namedtuple
import locale
from urllib.parse import urlparse
import csv
import base64
from mailersend import emails



locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')


Record = namedtuple('Record', ['cpf', 'email', 'phone', 'password'])


def get_project_root():
    # logger.info(f"get_project_root: {os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}")
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_latest_csv(output_path):
    """🔍 Encontra o arquivo CSV mais recente baseado no nome do padrão 'resultados_DD-MM-YYYY_HH-MM.csv'"""
    files = [f for f in os.listdir(output_path) if re.match(r'resultados_\d{2}-\d{2}-\d{4}_\d{2}-\d{2}\.csv', f)]
    
    if not files:
        print("⚠ Nenhum arquivo CSV encontrado!")
        return None
    files.sort(reverse=True)
    return os.path.join(output_path, files[0])

# def get_specific_folder(folder_name: str) -> str:
#     """
#     Retorna o caminho de uma pasta específica dentro do projeto.
    
#     :param folder_name: Nome da pasta específica.
#     :return: Caminho absoluto para a pasta.
#     """
#     project_root = get_project_root()
#     specific_folder = os.path.join(project_root, folder_name)
#     # logger.info(f"Caminho da pasta '{folder_name}': {specific_folder}")
#     return specific_folder

# def full_path(path):
#     # logger.info(f"full_path: {os.path.join(get_project_root(), path)}")
#     return get_project_root()



def remove_affix(prefix, suffix, text):
    if text.startswith(prefix) and text.endswith(suffix):
        return text[len(prefix):-len(suffix)]


def get_yesterdays_date():
    current = date.today()
    current_time = datetime.utcnow()
    time_format = '%Y-%m-%d'
    if current.day == 1:
        if current_time.hour <= 5:
            return date(
                current.year,
                current.month-1,
                (calendar.monthrange(current.year, current.month-1)[2])
            ).strftime(time_format)
        else:
            return date(
                current.year,
                current.month-1,
                (calendar.monthrange(current.year, current.month-1)[1])
            ).strftime(time_format)
    else:
        if current_time.hour <= 5:
            return date(
                current.year,
                current.month,
                current.day-2
            ).strftime(time_format)
        else:
            return date(
                current.year,
                current.month,
                current.day-1
            ).strftime(time_format)


def get_last_month():
    current = date.today()
    time_format = '%Y-%m'
    if current.day == 31:
        return date(
            current.year, current.month - 1,
            (calendar.monthrange(current.year, current.month-1)[1])
        ).strftime(time_format)
    else:
        return date(
            current.year, current.month-1, current.day
        ).strftime(time_format)


def format_json(dictionary):
    return json.dumps(dictionary, indent=4, sort_keys=True)




def find_file(name, path=None):
    if path is None:
        path = get_project_root()

    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


def find_file(name, path=None):
    """
    Procura por um arquivo específico em um diretório e seus subdiretórios.

    Args:
        name (str): Nome do arquivo a ser encontrado.
        path (str, optional): Diretório inicial para a busca. Se None, usa o diretório raiz do projeto.

    Returns:
        str: Caminho completo para o arquivo encontrado, ou None se não for encontrado.
    """
    if path is None:
        path = get_project_root()

    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

    return None


def filtrar_dados_csv(arquivo_csv):
    """
    Lê um arquivo CSV e filtra as linhas que possuem valores nos campos principais: CPF, email, telefone e nome.
    Adiciona o campo 'senha' com um valor padrão se não existir no CSV.

    Args:
        arquivo_csv (str): Caminho do arquivo CSV.

    Returns:
        list: Lista de dicionários com os dados filtrados.
    """
    dados_filtrados = []

    # Usando encoding='utf-8-sig' para remover a marca BOM
    with open(arquivo_csv, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file, delimiter=';')

        # Limpando os nomes das colunas
        if reader.fieldnames:
            reader.fieldnames = [campo.strip().lower() for campo in reader.fieldnames]

        for linha in reader:
            # Filtra linhas que têm valores nos campos principais
            if all(linha.get(campo, '').strip() for campo in ['cpf', 'email', 'telefone', 'nome']):
                dados_filtrados.append({
                    'cpf': linha['cpf'].strip(),
                    'email': linha['email'].strip(),
                    'telefone': linha['telefone'].strip(),
                    'nome': linha['nome'].strip(),
                    'senha': linha.get('senha', '123testePA').strip() 
                })

    return dados_filtrados


def gravar_dados_csv(arquivo_csv, usuario):
    """
    Grava dados de um único usuário em um arquivo CSV. 
    Se o arquivo não existir, cria com o cabeçalho apropriado.

    Args:
        arquivo_csv (str): Caminho do arquivo CSV.
        usuario (dict): Dicionário contendo os dados do usuário.
                        Exemplo: {'cpf': '...', 'email': '...', 'telefone': '...', 'nome': '...', 'senha': '...', 'sexo': '...'}
    """
    header = ['cpf', 'email', 'telefone', 'nome', 'senha', 'sexo']
    arquivo_existe = os.path.exists(arquivo_csv)
    with open(arquivo_csv, mode='a' if arquivo_existe else 'w', encoding='utf-8-sig', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=header, delimiter=';')
        if not arquivo_existe:
            writer.writeheader()
        writer.writerow(usuario)



def read_file_csv(csv_files, folder_path):
    """
    Reads the file and returns a list of tuples with the first and second values from each line.
    
    :param file_path: Path to the file relative to the project root.
    :return: List of tuples (first_value, second_value).
    """
    words = []
    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        
        print(f"\n📄 Lendo arquivo: {file}")
        
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter='\n')
            for row in reader:
                words.append(row[0])
    return words




from mailersend import emails

TOKEN = "mlsn.ad6d3272664ae99112234d7d77b671dd6efc13858529c002d8151de4cad652e6"


def send_email(file_name, file_path):
    mail_body = {} 

    mail_from = {
        "name": "Bot ML",
        "email": "MS_r9zLJe@trial-v69oxl5j90r4785k.mlsender.net",
    }

    recipients = [
        {
            "name": "Fabricio",
            "email": "fabcovalesci@gmail.com",
        }
    ]

    mailer = emails.NewEmail(TOKEN)
    
    # Definir remetente e destinatário
    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject("Discos disponíveis no Mercado Livre", mail_body)
    mailer.set_html_content("""
    <html>
    <body>
        <h1>Olá,</h1>
        <h2>Encontramos novos discos no Mercado Livre de acordo com sua pesquisa! 🛒🎶</h2>
        <p>Anexamos um arquivo Excel com todos os detalhes dos discos encontrados, incluindo títulos, preços e links diretos para compra.</p>
        <strong>Boas compras!</strong>
    </body>
    </html>
    """, mail_body)
    mailer.set_plaintext_content("Este é um e-mail com anexo contendo os discos encontrados.", mail_body)

    # Adicionar o arquivo Excel como anexo
    try:
        with open(file_path, "rb") as file:
            att_read = file.read()
            att_base64 = base64.b64encode(att_read)
            attachments = [
                {
                    "id": "my-attached-file",
                    "filename": file_name,
                    "content": att_base64.decode("ascii"),
                    "disposition": "attachment",
                    "type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                }
            ]
            mailer.set_attachments(attachments, mail_body)
    except Exception as e:
        print(f"Erro ao adicionar o anexo: {e}")
        return

    # Enviar o e-mail
    try:
        mailer.send(mail_body)
        print(f"E-mail enviado com sucesso para {recipients[0]['email']}")
    except Exception as e:
        print(f"Erro ao enviar o e-mail: {e}")