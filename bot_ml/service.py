import smtplib
import os
from email.message import EmailMessage
from utils import get_project_root

def send_email(smtp_server, port, to_email, subject, body, attachment_path):
    try:
        login = "botfab42@gmail.com"
        msg = EmailMessage()
        msg['From'] = login
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.set_content(body)

        # Anexar arquivo
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as f:
                file_data = f.read()
                file_name = os.path.basename(attachment_path)
            msg.add_attachment(file_data, maintype='application', subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=file_name)
        else:
            print("Arquivo de anexo não encontrado.")

        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls() 
            server.login(login, "$number42Bot")
            server.send_message(msg)
            print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")


file_exel = os.path.join(get_project_root(), "exel", 'Resultados-01-02-2025_04-59.xlsx')
print("=== ", file_exel)
send_email("smtp.gmail.com", 587, "fabcovalesci@gmal.com", "Assunto do Email", "Corpo do email", file_exel)
