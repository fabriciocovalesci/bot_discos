
from logger import logger
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
from decouple import config
from urllib.parse import urlparse
import csv

locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')


Record = namedtuple('Record', ['cpf', 'email', 'phone', 'password'])


def get_project_root():
    logger.info(f"get_project_root: {os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}")
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def full_path(path):
    logger.info(f"full_path: {os.path.join(get_project_root(), path)}")
    return get_project_root()



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



def read_file(file_path):
    """
    Reads the file and returns a list of tuples with the first and second values from each line.
    
    :param file_path: Path to the file relative to the project root.
    :return: List of tuples (first_value, second_value).
    """
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                cpf, email, phone, password = line.split(',')
                data.append(Record(cpf.strip(), email.strip(), phone.strip(), password.strip()))
    return data


