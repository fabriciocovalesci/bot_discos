import base64
from mailersend import emails
from utils import get_project_root

TOKEN = "mlsn.ad6d3272664ae99112234d7d77b671dd6efc13858529c002d8151de4cad652e6"


def send_email(file_name, file_path):
    mail_body = {} 

    mail_from = {
        "name": "Bot ML",
        "email": "MS_r9zLJe@trial-v69oxl5j90r4785k.mlsender.net",
    }

    recipients = [
        {
            "name": "Ailton",
            "email": "ailton.staniasky@gmail.com",
        },
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
