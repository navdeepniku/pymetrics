class Client():
    def __init__(self, ip, username, port, password, email, alerts=None):
        self.__ip = ip
        self.__username = username
        self.__port = port
        self.__password = password
        self.__email = email
        self.__alerts = alerts or []

    # getters
    def get_ip(self):
        return self.__ip

    def get_username(self):
        return self.__username

    def get_port(self):
        return self.__port

    def get_password(self):
        return self.__password

    def get_email(self):
        return self.__email

    def get_alerts(self):
        return self.__alerts

    # setters
    def set_ip(self, ip):
        self.__ip = ip

    def set_username(self, username):
        self.__username = username

    def set_port(self, port):
        self.__port = port

    def set_password(self, password):
        self.__password = password

    def set_email(self, email):
        self.__email = email

    def set_alerts(self, alert):
        self.__alerts.append(alert)


class Alert():
    def __init__(self, alert_type, limit):
        self.__alert_type = alert_type
        self.__limit = limit

    def set_alert_type(self, alert_type):
        self.__alert_type = alert_type

    def set_limit(self, limit):
        self.__limit = limit

    def get_alert_type(self):
        return self.__alert_type

    def get_limit(self):
        return self.__limit
