import xml.etree.ElementTree as ET
from threading import Thread
import datetime

from data_models.models import Client, Alert
from utils.custom_exceptions import FailedSSHClient
from utils.utils import ParamikoSSH, EncryptionHandle, DbConnection, SmtpSetup


# configure and execute on client
def client_handle(client):
    # init pramico
    try:
        ssh_client = ParamikoSSH().get_ssh_client(client.get_ip(), client.get_username(), client.get_password())

        # create remote dir on the client machine
        stdin, stdout, stderr = ssh_client.exec_command("mkdir -p /tmp/remotedir/")
        print(stdout.read())
        # get secure ftp connection and put client.py at remote location on the client
        sftp = ssh_client.open_sftp()
        sftp.put('client/client.py', '/tmp/remotedir/remoteclient.py')
        sftp.close()

        # execute remote client
        # virtualenv_exec_path for mac users virtualenv path if client is mac, else ensure virtualenv is installed in /usr/bin/
        stdin, stdout, stderr = ssh_client.exec_command("python -c'import platform; print (platform.system())'")
        client_os = stdout.read()
        virtualenv_exec_path = '/usr/local/bin/' if 'darwin' in client_os.lower() else ''
        required_metrics = [met.get_alert_type() for met in client.get_alerts()]
        stdin, stdout, stderr = ssh_client.exec_command(
            "if [ -e /tmp/remotedir/pyenv/bin/python ] ; then  echo 'env available'; else " + virtualenv_exec_path + "virtualenv /tmp/remotedir/pyenv; fi; source /tmp/remotedir/pyenv/bin/activate; pip install pycrypto psutil")
        stdout.read()
        # get key
        key = EncryptionHandle.gen_key()
        # pass one time AES key for encrypted client response
        stdin, stdout, stderr = ssh_client.exec_command(
            "/tmp/remotedir/pyenv/bin/python /tmp/remotedir/remoteclient.py " + key + ' "' + str(
                required_metrics) + '"')
        client_response = stdout.read()
        ParamikoSSH().close_ssh_client(ssh_client)
        enc_metrics = client_response
        # decrypt
        metrics = EncryptionHandle.aes_decrypt(key, enc_metrics).strip()
        metrics = eval(metrics)

        client_export_db(client, metrics)

        client_alerts(client, metrics)
    except FailedSSHClient as e:
        print (e)
    else:
        print "done for client :", client.get_ip()
        return "done"


# metrics write to DB
def client_export_db(client, metrics):
    print metrics
    try:
        con = DbConnection.get_connection()
        cur = con.cursor()
        sql = """insert into client_metrics (ip, metrics_timestamp, metrics) values ("{}", "{}", "{}")""".format(
            client.get_ip(), metrics['timestamp'], metrics['data'])
        cur.execute(sql)
        con.commit()
        con.close()
    except Exception as e:
        print "Error occurred while writing to MySQL due to: ", str(e)
        return 1
    else:
        print "results exported to MySQL for :", client.get_ip()
        return 0


# if alert? call smtp
def client_alerts(client, metrics):
    for alert in client.get_alerts():
        if alert.get_limit() == 'None':
            continue
        # consideration for alert: if metric value is more than threshold defined in server_config
        if int(metrics['data'][alert.get_alert_type()]) >= int(alert.get_limit().strip('%')):
            mail_text, mail_html = SmtpSetup.create_templete(client.get_ip(), alert.get_alert_type(),
                                                             metrics['data'][alert.get_alert_type()])
            try:
                SmtpSetup.send_mail(client.get_email(), mail_text, mail_html)
            except Exception as e:
                print "Could not send email due to ", str(e)
                return 1
            else:
                print ("Email sent to {}!".format(client.get_email()))
                return 0


# read server_config xml, returns list of client objects
def read_server_config():
    try:
        xml_file = ET.parse('configs/server_config.xml')
        xml_root = xml_file.getroot()
    except Exception as e:
        print ("Please check if config file is valid. Encountered error: ", str(e))
        return []
    clients = []
    for cl in xml_root.iter('client'):
        client_attr = cl.attrib
        # client object accepts: ip, username, port, password, email, alerts=[]
        ip, username, port, password, email = client_attr['ip'], client_attr['username'], client_attr['port'], \
                                              client_attr[
                                                  'password'], client_attr['mail']
        client_obj = Client(ip, username, port, password, email)

        for al in cl.iter('alert'):
            alert_attr = al.attrib
            alert_obj = Alert(alert_attr['type'], alert_attr['limit'])
            client_obj.set_alerts(alert_obj)

        clients.append(client_obj)
    return clients


if __name__ == "__main__":
    clients = read_server_config()
    # Get all clients and start a parallel thread

    for c in clients:
        t = Thread(target=client_handle, args=(c,))
        t.start()