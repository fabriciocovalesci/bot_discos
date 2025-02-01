from mailersend import emails

# Criar o objeto do e-mail
mailer = emails.NewEmail()

# Definir o corpo do e-mail
mail_body = {}

mail_from = {
    "name": "Seu Nome",
    "email": "seuemail@dominio.com",
}

recipients = [
    {
        "name": "Cliente",
        "email": "emaildocliente@dominio.com",
    }
]

reply_to = {
    "name": "Nome",
    "email": "responder@dominio.com",
}

# Definir os detalhes do e-mail
mailer.set_mail_from(mail_from, mail_body)
mailer.set_mail_to(recipients, mail_body)
mailer.set_subject("E-mail com Anexo", mail_body)
mailer.set_html_content("<p>Este é um e-mail com anexo.</p>", mail_body)
mailer.set_plaintext_content("Este é um e-mail com anexo.", mail_body)
mailer.set_reply_to(reply_to, mail_body)

# 📎 Adicionar anexo
with open("arquivo.pdf", "rb") as file:
    mailer.set_attachments(
        [
            {
                "content": file.read(),
                "filename": "arquivo.pdf",
                "disposition": "attachment",
            }
        ],
        mail_body,
    )

# Enviar o e-mail
mailer.send(mail_body)
