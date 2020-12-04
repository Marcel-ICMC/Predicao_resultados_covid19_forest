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
import re

# STANDARDIZED REFERENCE VALUES FROM PORTUGUESE DESCRIPTION

def standard_reference_value(str_description):
    lower_bound = 'None'
    upper_bound = 'None'
    ceiling_value = re.search(r'até (\-?\d+\.?\d*?\,?\d{,})',str_description.strip(), re.I)
    if ceiling_value:
        ceiling_value_str = ceiling_value.group(1)
        upper_bound = float(ceiling_value_str.replace('.','').replace(',','.'))
        return (lower_bound, upper_bound)
    ceiling_value_alt = re.search(r'inferior a (\-?\d+\.?\d*?\,?\d{,})',str_description.strip(), re.I)
    if ceiling_value_alt:
        ceiling_value_alt_str = ceiling_value_alt.group(1)
        upper_bound = float(ceiling_value_alt_str.replace('.','').replace(',','.'))
        return (lower_bound, upper_bound)
    ceiling_value_alt2 = re.search(r'menor que (\-?\d+\.?\d*?\,?\d{,})',str_description.strip(), re.I)
    if ceiling_value_alt2:
        ceiling_value_alt2_str = ceiling_value_alt2.group(1)
        upper_bound = float(ceiling_value_alt2_str.replace('.','').replace(',','.'))
        return (lower_bound, upper_bound)
    ceiling_value_symbom = re.search(r'< (\-?\d+\.?\d*?\,?\d{,})',str_description.strip(), re.I)
    if ceiling_value_symbom:
        ceiling_value_symbom_str = ceiling_value_symbom.group(1)
        upper_bound = float(ceiling_value_symbom_str.replace('.','').replace(',','.'))
        return (lower_bound, upper_bound)
    bottom_value = re.search(r'superior a (\-?\d+\.?\d*?\,?\d{,})',str_description.strip(), re.I)
    if bottom_value:
        bottom_value_str = bottom_value.group(1)
        lower_bound = float(bottom_value_str.replace('.','').replace(',','.'))
        return (lower_bound, upper_bound)
    bottom_value_alt = re.search(r'maior que (\-?\d+\.?\d*?\,?\d{,})',str_description.strip(), re.I)
    if bottom_value_alt:
        bottom_value_alt_str = bottom_value_alt.group(1)
        lower_bound = float(bottom_value_alt_str.replace('.','').replace(',','.'))
        return (lower_bound, upper_bound)
    bottom_value_symbol = re.search(r'> (\-?\d+\.?\d*?\,?\d{,})',str_description.strip(), re.I)
    if bottom_value_symbol:
        bottom_value_symbol_str = bottom_value_symbol.group(1)
        lower_bound = float(bottom_value_symbol_str.replace('.','').replace(',','.'))
        return (lower_bound, upper_bound)
    lower_upper_value = re.search(r'(\-?\d+\.?\d*?\,?\d{,}) a (\-?\d+\.?\d*?\,?\d{,})',str_description.strip(), re.I)
    if lower_upper_value:
        lower_bound = float(lower_upper_value.group(1).replace('.','').replace(',','.'))
        upper_bound = float(lower_upper_value.group(2).replace('.','').replace(',','.'))
        return (lower_bound, upper_bound)
    lower_upper_value_alt = re.search(r'(\-?\d+\.?\d*?\,?\d{,}) \- (\-?\d+\.?\d*?\,?\d{,})',str_description.strip(), re.I)
    if lower_upper_value_alt:
        lower_bound = float(lower_upper_value_alt.group(1).replace('.','').replace(',','.'))
        upper_bound = float(lower_upper_value_alt.group(2).replace('.','').replace(',','.'))
        return (lower_bound, upper_bound)
    return (lower_bound, upper_bound)

def is_abnormal_exam(str_description_result, str_description_ref_value):
    if re.search(r'não reagente|não detectado|não identificado|negativ|limpido',str_description_ref_value.strip(), re.I):
        return (str_description_result.strip().lower() != str_description_ref_value.strip().lower())
    standard_answer = standard_reference_value(str_description_ref_value)
    if standard_answer:
        lower_bound, upper_bound = standard_answer
    else:
        return 'Unknown'
    result = None
    try:
        result = float(str(str_description_result).replace('.',',').replace(',','.'))
    except:
        result_str = re.search(r'\-?\d+\.?\d*?\,?\d{,}',str(str_description_result),re.I)
        if result_str:
            result = float(str(result_str.group(0)).replace('.',',').replace(',','.'))
    # print('Parameters ', 'LB ', lower_bound, 'UB ', upper_bound, 'SBF ', should_be_found)
    # print('Result ',result)
    if not result:
        return 'Unknown'
    elif type(lower_bound) == float:
        if type(upper_bound) == float:
            return (result < lower_bound or result > upper_bound)
        else:
            return (result < lower_bound)
    elif type(upper_bound) == float:
        return (result > upper_bound)
    return 'Unknown'

def update_status_exams():
    cursor = cursorConexao()
    cursor.execute('SELECT ID, ID_PATIENT, DE_RESULTADO, DE_VALOR_REFERENCIA FROM covidFapespSimple.exame_laboratorial;')
    data = cursor.fetchall()
    for id_exam, id_patient, str_description_result, str_description_ref_value in data:
        if len(str_description_result) > 3 and len(str_description_ref_value) > 3:
            result = is_abnormal_exam(str_description_result, str_description_ref_value)
            lower_bound, upper_bound = standard_reference_value(str_description_ref_value)
            cursor_update = cursorConexao()
            cursor_update.execute('INSERT INTO covidFapespSimple.parse_exame_laboratorial (ID_EXAME, ID_PATIENT, LOWER_BOUND, UPPER_BOUND, IS_ABNORMAL) VALUES ("{}","{}","{}","{}","{}")'.format(id_exam, id_patient, lower_bound, upper_bound, result))
            cursor_update.close()
    cursor.close()

if __name__ == "__main__":
    # TEST FUNCTION
    tests = [
        ('34,5','31,0 a 36.0',False),
        ('34,5','31,0 a 33,0',True),
        ('','','Unknown'),
        ('','3,0 a 4,0','Unknown'),
        ('não reagente','3,0 a 4,0','Unknown'),
        ('3,0','não reagente',True),
        ('3,0','Normais','Unknown'),
        ('3','< 4',False),
        ('3','> 4',True),
        ('3','Inferior a 4',False),
        ('3','Superior a 4',True),
        ('não reagente','Não reagente',False)
    ]
    for str_description_result, str_description_ref_value, answer in tests:
        res = is_abnormal_exam(str_description_result, str_description_ref_value) == answer
        if not res:
            print('Error with test ',str_description_result, str_description_ref_value, answer)