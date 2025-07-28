import smtplib, json
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText


smtp_server = 'smtp.office365.com'
smtp_port = 587
smtp_username = 'nao-responda@grupotapajos.com.br'
smtp_password = 'Pab67529!'
de = 'nao-responda@grupotapajos.com.br'


def send_mail_aprovado(para, nome, vaga, loja, horario, escala, modalidade, data_exame):

    assunto = 'Você foi aprovado(a) - Processo Seletivo Grupo Tapajós 🎉'
    with open("./email/candidato_aprovado.html", 'r', encoding='utf-8') as arquivo:
        conteudo_html = arquivo.read()

    corpo_html = conteudo_html.replace("[Nome do Candidato]", nome, -1)
    corpo_html = corpo_html.replace("[Nome da Vaga]", vaga, -1)
    corpo_html = corpo_html.replace("[Nome da Loja]", loja, -1)
    corpo_html = corpo_html.replace("[Horário]", horario, -1)
    corpo_html = corpo_html.replace("[Escala]", escala, -1)
    corpo_html = corpo_html.replace("[Presencial/Híbrido]", modalidade, -1)
    corpo_html = corpo_html.replace("[exame_data]", data_exame, -1)

    mensagem = MIMEMultipart()
    mensagem['From'] = smtp_username
    mensagem['To'] = para
    mensagem['Subject'] = assunto

    # Adicionando anexo em PDF
    arquivo_anexo = open('./email/assets/LISTA_DOCUMENTOS_ATUALIZADA.pdf', 'rb')
    anexo = MIMEApplication(arquivo_anexo.read(), Name='LISTA_DOCUMENTOS_ATUALIZADA.pdf')
    anexo['Content-Disposition'] = 'attachment; filename="%s"' % 'LISTA_DOCUMENTOS_ATUALIZADA.pdf'
    mensagem.attach(anexo)
    # Adicionando o corpo HTML do e-mail
    corpo = MIMEText(corpo_html, 'html')
    mensagem.attach(corpo)

    # Conectando ao servidor SMTP
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(de, para, mensagem.as_string())

    server.quit()
    return {'status': 'ok', 'mensagem': 'E-mail enviado com sucesso'}








def send_mail_recusado(para, nome, vaga):

    assunto = 'Agradecimento pela sua participação - Grupo Tapajós'
    with open("./email/candidato_reprovado.html", 'r', encoding='utf-8') as arquivo:
        conteudo_html = arquivo.read()

    corpo_html = conteudo_html.replace("[nome_candidato]!", nome, -1)
    corpo_html = corpo_html.replace("[Nome da Vaga]", vaga, -1)
    mensagem = MIMEMultipart()
    mensagem['From'] = smtp_username
    mensagem['To'] = para
    mensagem['Subject'] = assunto
    # Adicionando o corpo HTML do e-mail
    corpo = MIMEText(corpo_html, 'html')
    mensagem.attach(corpo)

    # Conectando ao servidor SMTP
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(de, para, mensagem.as_string())

    server.quit()
    return {'status': 'ok', 'mensagem': 'E-mail enviado com sucesso'}



def send_mail_entrevista(para, nome, vaga, dia_hora_entevista, escala, salario):

    assunto = 'Entrevista Agendada - Processo Seletivo Grupo Tapajós'
    with open("./email/candidato_entrevista.html", 'r', encoding='utf-8') as arquivo:
        conteudo_html = arquivo.read()

    corpo_html = conteudo_html.replace("[Nome do Candidato]", nome, -1)
    corpo_html = corpo_html.replace("[Nome da Vaga]", vaga, -1)
    corpo_html = corpo_html.replace("[dia_hora_entevista]", dia_hora_entevista, -1)
    corpo_html = corpo_html.replace("[Escala]", escala, -1)
    corpo_html = corpo_html.replace("[Salário]", salario, -1)

    mensagem = MIMEMultipart()
    mensagem['From'] = smtp_username
    mensagem['To'] = para
    mensagem['Subject'] = assunto
    # Adicionando o corpo HTML do e-mail
    corpo = MIMEText(corpo_html, 'html')
    mensagem.attach(corpo)
    # Conectando ao servidor SMTP
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(de, para, mensagem.as_string())

    server.quit()
    return {'status': 'ok', 'mensagem': 'E-mail enviado com sucesso'}


