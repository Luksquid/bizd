import oracledb
import os 
import pandas as pd
import numpy as np  
import re
from datetime import datetime
import traceback
import sys

sys.tracebacklimit = 0

class Backup:
    def __init__(self):
        table_df = pd.read_csv('files_info.csv')

        USER = "kalamarskil"
        PASSWORD = "RybAk012"
        DSN = "213.184.8.44:1521/orcl"

        self.connection = oracledb.connect(user=USER, password=PASSWORD, dsn=DSN)

        for i in range(8):
            self.insert_data_from_csv(table_df.iloc[i])

    def insert_data_from_csv(self, table_df):
        file_name = table_df['files']
        table_name = table_df['tables']
        archive_name = table_df['archives']

        cursor = self.connection.cursor()
        table_data = pd.read_csv(file_name)
        columns = str(tuple(table_data.columns)).replace("'","")
        values_index = str(tuple([':'+str(i+1) for i in range(len(table_data.columns))])).replace("'","")

        query = F"SELECT NVL(MAX(ID), 0) FROM {table_name}"
        
        cursor.execute(query)
        last_id = cursor.fetchone()[0] 

        try:

            for i ,row in table_data.iterrows():
                values = list(row.values)
                values[0] = last_id + i + 1
                table_data.loc[i,'ID'] = values[0]

                for i in range(len(values)):
                    try:
                        values[i] = float(values[i])
                    except:
                        pass
                
                values = tuple(values)

                cursor.execute(
                    "INSERT INTO " + table_name + " " + columns + " VALUES " + values_index,
                    values
                )
                    
            if len(table_data.index) > 0:
                table_data.to_csv(archive_name, mode='a', header=None, index=False)
                empty_df = pd.DataFrame(columns=table_data.columns)
                empty_df.to_csv(file_name, index=False)
                
                with open('./logs.txt', 'a', encoding='utf-8') as file:
                    now_time = datetime.now()
                    now_time = now_time.replace(microsecond=0)
                    file.write(str(now_time) + '\n')
                    file.write(f'Plik: {file_name} \n')
                    file.write(f'Poprawnie przesłano dane\n')
                    file.write('\n')

        except:
            with open('./logs.txt', 'a', encoding='utf-8') as file:
                now_time = datetime.now()
                now_time = now_time.replace(microsecond=0)
                file.write(str(now_time) + '\n')
                file.write(f'Plik: {file_name} \n')
                file.write(f'Błąd: {str(Exception)}\n')
                file.write('Szczegóły błędu:\n')
                traceback.print_exc(file=file)
                file.write('\n')

        self.connection.commit()

backup = Backup()