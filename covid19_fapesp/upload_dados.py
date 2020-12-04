# Copyright (c) 2020 Danilo Panzeri Nogueira Carlotti

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from connection_mysql import cursorConexao
from standard_reference_value import is_abnormal_exam, standard_reference_value
from validator import check_encoding_separators, check_separator
import pandas as pd
import sys

columns_patient_db = {
    'IC_SEXO':'sexo',
    'CD_PAIS':'pais',
    'CD_INSTITUICAO':'institution',
    'CD_UF':'uf',
    'CD_CEP':'cep',
    'CD_MUNICIPIO':'municipio'
}
columns_patient_insert = ['IC_SEXO','CD_PAIS','CD_INSTITUICAO','CD_UF','CD_MUNICIPIO']

columns_patient_db_ALL = ['ID_PACIENTE','IC_SEXO','AA_NASCIMENTO','CD_PAIS','CD_UF','CD_MUNICIPIO','CD_CEPREDUZIDO']
columns_exame_db_ALL = ['ID_PACIENTE','DT_COLETA','DE_ORIGEM','DE_EXAME','DE_ANALITO','DE_RESULTADO','CD_UNIDADE','DE_VALOR_REFERENCIA']
columns_desfecho_db_ALL = ['ID_PACIENTE','ID_CLINICA','DE_CLINICA','DT_DESFECHO','DE_DESFECHO']

id_vars_patient = {}

def insert_data_outcome(data):
    cursor = cursorConexao()
    query = 'INSERT INTO covidFapesp.desfecho (ID_PACIENTE, ID_CLINICA, DE_CLINICA, DT_DESFECHO, DE_DESFECHO) VALUES ("{}","{}","{}","{}","{}")'.format(str(data['ID_PACIENTE']).replace('\\',' '),str(data['ID_CLINICA']).replace('\\',' '),str(data['DE_CLINICA']).replace('\\',' '),str(data['DT_DESFECHO']).replace('\\',' '),data['DE_DESFECHO'].replace('\\',' '))
    cursor.execute(query)
    cursor.close()

def insert_data_exams(datas):
    cursor = cursorConexao()
    tuples_from_data = [(data['ID_PACIENTE'],data['DT_COLETA'],data['DE_ORIGEM'].replace('\\',' '),data['DE_EXAME'].replace('\\',' '),data['DE_ANALITO'].replace('\\',' '),data['DE_RESULTADO'].replace('\\',' '),data['CD_UNIDADE'].replace('\\',' '),data['DE_VALOR_REFERENCIA'].replace('\\',' ')) for data in datas]
    tuples_string = ''
    for tuple_d in tuples_from_data:
        tuples_string += str(tuple_d) + ' , '
    tuples_string = tuples_string[:-2]
    query = 'INSERT INTO covidFapesp.exame_laboratorial (ID_PACIENTE, DT_COLETA, DE_ORIGEM, DE_EXAME, DE_ANALITO, DE_RESULTADO, CD_UNIDADE, DE_VALOR_REFERENCIA) VALUES {}'.format(tuples_string)
    cursor.execute(query)
    cursor.close()

def insert_data_patient(data):
    for c in columns_patient_insert:
        if data[c] not in id_vars_patient:
            new_cursor = cursorConexao()
            new_cursor.execute('INSERT INTO covidFapesp.{} ({}) values ("{}")'.format(columns_patient_db[c], columns_patient_db[c], data[c]))
            new_cursor.execute('SELECT LAST_INSERT_ID() from covidFapesp.{};'.format(columns_patient_db[c]))
            id_var = new_cursor.fetchone()[0]
            new_cursor.close()
            id_vars_patient[data[c]] = id_var
    try:
        cursor = cursorConexao()
        cursor.execute('INSERT INTO covidFapesp.patient (ID, IC_SEXO, AA_NASCIMENTO, CD_PAIS, CD_INSTITUICAO, CD_UF, CD_CEP, CD_MUNICIPIO) values ("{}", {}, "{}", {}, {}, {}, "{}", {})'.format(data['ID_PACIENTE'].replace('\\',' '),id_vars_patient[data['IC_SEXO']],data['AA_NASCIMENTO'].replace('\\',' '),id_vars_patient[data['CD_PAIS']],id_vars_patient[data['CD_INSTITUICAO']],id_vars_patient[data['CD_UF']],data['CD_CEP'],id_vars_patient[data['CD_MUNICIPIO']]))
        cursor.close()
    except Exception as e:
        print(e)

method_dictionary = {
    'exame':insert_data_exams,
    'paciente':insert_data_patient,
    'desfecho':insert_data_outcome
}

columns_dictionary = {
    'exame':columns_exame_db_ALL,
    'paciente':columns_patient_db_ALL,
    'desfecho':columns_desfecho_db_ALL
}

def parse_data(csv_path, method, institution):
    encoding_csv = check_encoding_separators(csv_path)
    separator = check_separator(csv_path,encoding_csv)
    df_data = pd.read_csv(csv_path,sep=separator,encoding=encoding_csv)
    df_data.columns = df_data.columns.str.upper()
    df_data.fillna('nan',inplace=True)
    if method == 'paciente':
        new_cursor = cursorConexao()
        for c in columns_patient_insert:
            new_cursor.execute('SELECT id, {} from covidFapesp.{}'.format(columns_patient_db[c],columns_patient_db[c]))
            is_found = new_cursor.fetchall()
            for id_v, var in is_found:
                id_vars_patient[var] = id_v
    counter = len(df_data.index)
    rows_exams = []
    for _,row in df_data.iterrows():
        if encoding_csv == 'latin-1':
            data = {k.upper():str(row[k]).decode('latin-1').encode('utf-8').decode('utf-8') for k in df_data.columns}
            print(data)
            sys.exit()
        else:
            data = {k.upper():row[k] for k in df_data.columns}
        # INSERT MISSING DATA
        data['CD_INSTITUICAO'] = institution
        for c in columns_dictionary[method]:
            if c not in data:
                data[c] = 'nan'
        try:
            if method == 'exame':
                if len(rows_exams) > 500:
                    method_dictionary[method](rows_exams)
                    rows_exams = []
                else:
                    rows_exams.append(data)
            else:        
                method_dictionary[method](data)
        except Exception as e:
            print(e)
            sys.exit()
        print('Faltam ',counter)
        counter -= 1

if __name__ == "__main__":
    parse_data(sys.argv[1],sys.argv[2],sys.argv[3])