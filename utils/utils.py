import binascii
import email.utils
# smtp imports
import smtplib
from StringIO import StringIO
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import MySQLdb
import paramiko
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA

from configs.config import db_host, db_username, db_name, db_password
from configs.config import smtp_username, smtp_password, smtp_host, smtp_port, smtp_sender_email, smtp_sender_name
from custom_exceptions import FailedSSHClient


class ParamikoSSH:
    # generate RSA keypair
    key = RSA.generate(2048)
    pubkey = key.publickey()
    # export will copy the key to a variable as string
    # exporting to Openssh format to add in authorized_keys
    public_key = pubkey.exportKey('OpenSSH')
    private_key = key.exportKey()
    paramiko_key = paramiko.RSAKey.from_private_key(StringIO(private_key))

    def get_ssh_client(self, hostname, username, password):
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=hostname, username=username, password=password)
            # with key: ssh_client.connect(hostname='localhost', username='navdeep', pkey=paramiko_key)
            ssh_client.invoke_shell()
            return ssh_client
        except Exception as e:
            raise FailedSSHClient(hostname, e)

    def close_ssh_client(self, ssh_client):
        ssh_client.close()


class EncryptionHandle():
    @staticmethod
    def gen_key():
        # AES Encryption, generating random key for AES
        return binascii.hexlify(Random.get_random_bytes(16))

    @staticmethod
    def aes_decrypt(key, enc_msg):
        # get cipher object
        cipher = AES.new(key)
        return cipher.decrypt(enc_msg).decode('utf-8')


class DbConnection():
    @staticmethod
    def get_connection():
        con = MySQLdb.connect(db_host, db_username, db_password, db_name)
        return con


class SmtpSetup():
    @staticmethod
    def send_mail(recipient, mail_text, mail_html):
        # Using AWS SES
        # If your account is still in the sandbox, recipient address must be verified.

        # The subject line of the email.
        subject = 'Alert from monitoring App'

        # Create the body of the message (a plain-text and an HTML version).

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = email.utils.formataddr((smtp_sender_name, smtp_sender_email))
        msg['To'] = recipient

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(mail_text, 'plain')
        part2 = MIMEText(mail_html, 'html')
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        server = smtplib.SMTP_SSL(smtp_host, smtp_port)
        server.ehlo()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_sender_email, recipient, msg.as_string())
        server.close()

    @staticmethod
    def create_templete(ip, alert_type, alert_value):
        text = '\r\n'.join([
            "Monitoring App Alerts",
            """You are receiving this email because your server host {} has {} value {}""".format(ip, alert_type,
                                                                                                  alert_value)
        ])
        html = '\n'.join([
            "<html>",
            "<head></head>",
            "<body>",
            "<h1>Monitoring App Alerts</h1>",
            """<p>You are receiving this email because your server host {} has {} value {}</p>""".format(ip, alert_type,
                                                                                                         alert_value),
            "</body>",
            "</html>"
        ])

        return text, html
