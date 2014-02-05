import splunklib.client as splunk_client
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('.splunkrc')

host = config.get('Splunk', 'host')
port = config.getint('Splunk', 'port')
username = config.get('Splunk', 'username')
password = config.get('Splunk', 'password')

splunk_connection = splunk_client.connect(host=host, port=port, username=username, password=password)

print splunk_connection.splunk_version