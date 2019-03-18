import json


with open('config.json') as f:
    j = json.load(f)
    TABLE = j['table']
    MYSQL_NAME = j['mysql_name']
    MYSQL_PASSWORD = j['mysql_password']
    DATABASE_NAME = j['database_name']
    FILENAME=j['xlsx_file']