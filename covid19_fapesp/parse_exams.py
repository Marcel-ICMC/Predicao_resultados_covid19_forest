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

def parse_exams():
    cursor = cursorConexao()
    cursor.execute('SELECT count(*) from covidFapesp.exame_laboratorial;')
    len_table_exams = cursor.fetchone()[0]
    for i in range(1135498,len_table_exams,2000):
        print('Faltam ',len_table_exams-i)
        cursor.execute('SELECT id, ID_PACIENTE, DE_RESULTADO, DE_VALOR_REFERENCIA from covidFapesp.exame_laboratorial LIMIT {}, 500'.format(str(i)))
        cursor_update = cursorConexao()
        rows_data = []
        for id_exam, id_p, resultado, valor_ref in cursor.fetchall():
            if len(str(resultado)) > 3 and len(str(valor_ref)) > 3:
                result = is_abnormal_exam(resultado, valor_ref)
                lower_bound, upper_bound = standard_reference_value(valor_ref)
                rows_data.append((id_exam, id_p, str(lower_bound).replace('\\',' '), str(upper_bound).replace('\\',' '), str(result).replace('\\',' ')))
        tuples_from_data = [tuple_d for tuple_d in rows_data]
        tuples_string = ''
        for tuple_d in tuples_from_data:
            tuples_string += str(tuple_d) + ' , '
        tuples_string = tuples_string[:-2]
        cursor_update.execute('INSERT INTO covidFapesp.parse_exame_laboratorial (ID_EXAME, ID_PACIENTE, LOWER_BOUND, UPPER_BOUND, IS_ABNORMAL) VALUES {}'.format(tuples_string))
        cursor_update.close()

if __name__ == "__main__":
    parse_exams()