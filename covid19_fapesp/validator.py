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

from docx import Document
import pandas as pd
import random
import re
import sys

columns_dictionary = {
    'paciente' : ['ID_PACIENTE','IC_SEXO','AA_NASCIMENTO','CD_PAIS','CD_UF','CD_MUNICIPIO','CD_CEPREDUZIDO'],
    'exame' : ['ID_PACIENTE','DT_COLETA','DE_ORIGEM','DE_EXAME','DE_ANALITO','DE_RESULTADO','CD_UNIDADE','DE_VALOR_REFERENCIA'],
    'desfecho' : ['ID_PACIENTE','DT_ATENDIMENTO','DE_TIPO_ATENDIMENTO','ID_CLINICA','DE_CLINICA','DT_DESFECHO','DE_DESFECHO']
}

def check_separator(csv_path, encoding):
    for sep in [';','|',',']:
        df_data = pd.read_csv(csv_path,sep=sep,nrows=5,encoding=encoding)
        df_data.columns = df_data.columns.str.upper()
        if 'ID_PACIENTE' in df_data.columns:
            return sep
    return '|'

def check_encoding_separators(csv_path):
    for sep in [';','|',',']:
        try:
            df_data = pd.read_csv(csv_path,sep=sep,nrows=5)
            return 'utf-8'
        except:
            try:
                df_data = pd.read_csv(csv_path,sep=sep,encoding='latin-1',nrows=5)
                return 'latin-1'
            except:
                pass
    return False

def check_columns(csv_path, type_f, encoding,separator):
    df_data = pd.read_csv(csv_path,sep=separator,encoding=encoding, nrows=5)
    df_data.columns = df_data.columns.str.upper()
    missing_columns = []
    for c in columns_dictionary[type_f]:
        if c not in df_data.columns:
            missing_columns.append(c)
    return missing_columns

def check_anonymity_id(csv_path, encoding,separator):
    df_data = pd.read_csv(csv_path, sep=separator, encoding=encoding)
    df_data.columns = df_data.columns.str.upper()
    ids_not_hashed = []
    dic_ids = {}
    for _, row in df_data.iterrows():
        if not (type(row['ID_PACIENTE']) == str and len(row['ID_PACIENTE']) > 10 and re.search(r'\d\w*?\d\w|\w\d*?\w\d',row['ID_PACIENTE'])):
            ids_not_hashed.append(row['ID_PACIENTE'])
        else:
            if row['ID_PACIENTE'] not in dic_ids:
                dic_ids[row['ID_PACIENTE']] = 1
            else:
                dic_ids[row['ID_PACIENTE']] += 1
    repeat_ids = []
    for k, v in dic_ids.items():
        if v > 1:
            repeat_ids.append((k,v))
    return (ids_not_hashed, repeat_ids)

def check_anonymity_patient(csv_path, encoding,separator):
    df_data = pd.read_csv(csv_path,  sep=separator, encoding=encoding)
    df_data.columns = df_data.columns.str.upper()
    dicionario_dados = {k:{} for k in columns_dictionary['paciente'][1:]}
    for _, row in df_data.iterrows():
        for c in columns_dictionary['paciente'][1:]:
            if str(row[c]) == 'nan':
                continue
            if str(row[c]) not in dicionario_dados[c]:
                dicionario_dados[c][str(row[c])] = []
            dicionario_dados[c][str(row[c])].append(1)
    list_var_identifiable = []
    for var, dic_var in dicionario_dados.items():
        for subvar, list_items in dic_var.items():
            if len(list_items) < 5:
                list_var_identifiable.append('O valor da instância {} referente a {} ocorre menos de 5 vezes entre os pacientes.\n\n'.format(var,subvar))
    return list_var_identifiable

def check_anonymity_year(csv_path, encoding,separator):
    df_data = pd.read_csv(csv_path,  sep=separator, encoding=encoding)
    df_data.columns = df_data.columns.str.upper()
    non_anonimized_rows = []
    for _, row in df_data.iterrows():
        try:
            if int(row['AA_NASCIMENTO']) <= 1930:
                non_anonimized_rows.append('\n\nPaciente com id {} tem como ano de nascimento {}.\n'.format(row['ID_PACIENTE'],row['AA_NASCIMENTO']))
        except:
            pass
    if len(non_anonimized_rows):
        non_anonimized_rows.append('\n')
    return non_anonimized_rows

def report_validator(csv_path, type_f):
    nome_arquivo = csv_path.split('/')[-1]
    report = ['Este é o relatório sobre o arquivo {}\n\n'.format(nome_arquivo)]
    encoding = check_encoding_separators(csv_path)
    separator = check_separator(csv_path, encoding)
    if not encoding:
        report.append('Este arquivo não está nos formatos latin-1 ou utf-8, portanto é impossível validá-lo.\n\n')
    else:
        if encoding != 'utf-8':
            report.append('Este arquivo não está em codificação utf-8.\n\n')
        if separator != '|':
            report.append('Este arquivo tem separador diferente de "|".\n\n')
        missing_columns = check_columns(csv_path, type_f, encoding, separator)
        for c in missing_columns:
            report.append('Está faltando a coluna {} prevista no dicionário de dados\n\n'.format(c))
        ids_not_hashed, repeat_ids = check_anonymity_id(csv_path, encoding, separator)
        if len(ids_not_hashed):
            report.append('Este arquivo possui ids que não estão no formato esperado de hash alfanumérico\n')
            if len(ids_not_hashed) > 5:
                k = 5
            else:
                k = len(ids_not_hashed)
            report.append('São exemplos desses id\'s: {}\n\n'.format(','.join(random.sample(ids_not_hashed,k=k))))
        if len(repeat_ids) and type_f == 'paciente':
            report.append('Este arquivo possui ids repetidos:\n')
            for id_r, n in repeat_ids:
                report.append('ID {} aparece repetido {} vezes.\n'.format(id_r,str(n)))
            report.append('\n')
    if type_f == 'paciente':
        report += check_anonymity_patient(csv_path, encoding, separator)
        report += check_anonymity_year(csv_path,encoding, separator)
    doc = Document()
    for r in report:
        doc.add_paragraph(r)
    doc.save('Relatório do validador sobre arquivo {}.docx'.format(nome_arquivo))

if __name__ == "__main__":
    # csv_path e tipo de arquivo
    report_validator(sys.argv[1], sys.argv[2])