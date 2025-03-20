import csv

def buscar_nome_no_csv(nome, arquivo_csv):
    """Retorna True se encontrar o nome no CSV, senão retorna False."""
    with open(arquivo_csv, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for linha in reader:
            if linha and nome.strip().lower() == linha[0].strip().lower():
                return True
    return False

# Exemplo de uso:
arquivo = "ja_coletados.csv"
nome_procurado = "Banda Reflexu's.lp Da Mãe África.novo"

if buscar_nome_no_csv(nome_procurado, arquivo):
    print("✅ Nome encontrado no CSV!")
else:
    print("❌ Nome NÃO encontrado no CSV.")

# teste
