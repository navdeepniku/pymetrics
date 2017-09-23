import sys
import psutil
from Crypto.Cipher import AES
import time, datetime


class EncryptionHandle():
    @staticmethod
    def pad_msg_aes(msg):
        # padding message with whitespaces
        return msg + (16 - len(msg) % 16) * ' '

    @staticmethod
    def aes_encrypt(key, msg):
        # pad msg for aes
        padded_msg = EncryptionHandle.pad_msg_aes(msg)
        # get cipher object
        cipher = AES.new(key)
        return cipher.encrypt(padded_msg)


class MetricsFormulae():
    # get metrics using psutils for CPU and memory % utilized
    @staticmethod
    def cpu_percent():
        return psutil.cpu_percent(interval=1)

    @staticmethod
    def mem_percent():
        return psutil.virtual_memory()[2]

    @staticmethod
    def uptime():
        return time.time() - psutil.boot_time()  # uptime in seconds

        # placeholder for other metrics


if __name__ == "__main__":
    o_stdout = sys.stdout
    sys.stdout = open('/tmp/remotedir/client_logs', 'w')
    # get required metrics list
    required_metrics = eval(sys.argv[2])
    # get key from args
    key = sys.argv[1]
    d = {}
    for metric in required_metrics:
        d[metric] = eval("MetricsFormulae." + metric + "()")
    d = {"timestamp": datetime.datetime.now(), "data": d}
    # encrypt metrics
    metrics_data = str(d)
    enc_metrics = EncryptionHandle.aes_encrypt(key, metrics_data)
    # write metrics to stdout
    sys.stdout = o_stdout
    sys.stdout.write(enc_metrics)
