import postgresql
import pyodbc
import os
import sys

class Database():
    def __init__(self, db_name, db_type):
        self.db_name = db_name
        self.db_type = db_type
        if self.db_type == 'postgre':
            self.db = postgresql.open('pq://root:root@localhost/{}'.format(self.db_name))
        elif self.db_type == 'mssql':
            self.db = pyodbc.connect('DRIVER=ODBC Driver 13 for SQL Server;SERVER=TOKARENKO\SQLEXPRESS;'
                                    'DATABASE={}; UID=sa; PWD=saPass1'.format(self.db_name))


    def get_process_data(self, card_id):
        '''Возвращает словарь, где ключом является название этапа процесса,
    а значением - список имен пользователей, от которых требуется действие
    по процессу. Если процесс не запущен, возвращается соответствующее
    уведомление.'''
        users_id_list = []
        dic = dict()
        if self.db_type == 'postgre':
            users_id = self.db.query("select user_id, name from wf_assignment where card_id = '{}' and"
                                " finished is null and user_id is not null".format(card_id))
        elif self.db_type == 'mssql':
            query = self.db.cursor()
            query.execute("select user_id, name from wf_assignment where card_id = '{}' and"
                          " finished is null and user_id is not null".format(card_id))
            users_id = []
            for row in query:
                users_id.append(row)
        try:
            assert bool(users_id) is True, 'There are no active process with current card'
            for users in users_id:
                if self.db_type == 'postgre':
                    key = users['name'].strip()
                    user_id = (str(users[0]))
                    user_name = self.db.query("select name from sec_user where id = '{}'".format(user_id))
                    user_name = (user_name[0][0]).strip()
                elif self.db_type == 'mssql':
                    key = (users.name).strip()
                    user_id = users.user_id
                    query.execute("select name from sec_user where id = '{}'".format(user_id))
                    for row in query:
                        user_name = row.name.strip()
                users_id_list.append(user_name)
            dic[key] = users_id_list
            return dic
        except AssertionError as err:
            return ("{0} - Assert error: {1}".format(
                os.path.basename(sys.argv[0]), err))


    def get_card_id_from_assignment_id(self, assignment_id):
        if self.db_type == 'postgre':
            card_id = self.db.query("select card_id from wf_assignment where id = '{}'".format(assignment_id))
            return str(card_id[0][0])
        elif self.db_type == 'mssql':
            query = self.db.cursor()
            query.execute("select card_id from wf_assignment where id = '{}'".format(assignment_id))
            for row in query:
                card_id = row
            return card_id.card_id


    def get_proc_states(self, assignment_id):
        if self.db_type == 'postgre':
            proc_id = self.db.query("select proc_id from wf_assignment where id = '{}'".format(assignment_id))
            proc_id = str(proc_id[0][0])
            proc_states = self.db.query("select states from WF_PROC where id = '{}'".format(proc_id))
            proc_states = str(proc_states).strip("(),' []").split(',')
            proc_states = [x.strip() for x in proc_states]
            return proc_states
        elif self.db_type == 'mssql':
            query = self.db.cursor()
            query.execute("select proc_id from wf_assignment where id = '{}'".format(assignment_id))
            for row in query:
                proc_id = row.proc_id
            query.execute("select states from WF_PROC where id = '{}'".format(proc_id))
            for row in query:
                proc_states = str(row).strip("(),' []").split(',')
                proc_states = [x.strip() for x in proc_states]
            return proc_states


    def get_states_from_design(self, assignment_id):
        try:
            if self.db_type == 'postgre':
                proc_id = self.db.query("select proc_id from wf_assignment where id = '{}'".format(assignment_id))
                proc_id = str(proc_id[0][0])
                design_id = self.db.query("select design_id from wf_proc where id = '{}'".format(proc_id))
                design_id = str(design_id[0][0])
                assert design_id != 'None', 'there are no disign for this card'
                content = self.db.query("select content from wf_design_file where design_id = '{}'"
                                   " and name = 'messages_ru.properties'".format(design_id))
                content = str(content[0][0])
            elif self.db_type == 'mssql':
                query = self.db.cursor()
                query.execute("select proc_id from wf_assignment where id = '{}'".format(assignment_id))
                for row in query:
                    proc_id = row.proc_id
                query.execute("select design_id from wf_proc where id = '{}'".format(proc_id))
                for row in query:
                    design_id = row.design_id
                assert design_id is not None, 'there are no disign for this card'
                query.execute("select content from wf_design_file where design_id = '{}'"
                              " and name = 'messages_ru.properties'".format(design_id))
                for row in query:
                    content = row.content
            states_list = []
            content = content.split('\n')
            for item in content:
                if not item.startswith('#'):
                    item = item.strip().split('=')
                    if '.' not in item[0]:
                        states_list.append(item)
            states_dict = dict()
            for couple in states_list:
                if len(couple) == 2:
                    if couple[0] != couple[1]:
                        states_dict[couple[0]] = couple[1].replace('\\', '')
            return states_dict
        except AssertionError:
            return None
