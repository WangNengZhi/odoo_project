from datetime import timedelta
import logging
import pymssql
from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class TemplateMachineRecord(models.Model):
    _name = 'template_machine_record'
    _description = '模板机器记录'
    _rec_name = 'FileName'
    _order = 'StartTime desc'

    MachineID = fields.Char(string='机器标识')
    FileName = fields.Char(string="文件名称")
    FileUUD = fields.Char(string="文件UUD")
    FileStitches = fields.Integer(string="文件针")
    BaseLineUse = fields.Integer(string="基线使用")
    ProcCounts = fields.Integer(string="程序计数")
    ProcTime = fields.Integer(string="程序时间")
    EndStitch = fields.Integer(string="结束针")
    NodeDistance = fields.Integer(string="节点距离")
    StartTime = fields.Datetime(string="开始时间")   #
    CreateTime = fields.Datetime(string="创建时间")  #


    def get_mssql_db_configuration(self):
        sql_server_host = self.env.company.sql_server_host
        sql_server_user = self.env.company.sql_server_user
        sql_server_password = self.env.company.sql_server_password
        sql_server_database = self.env.company.sql_server_database
        return sql_server_host, sql_server_user, sql_server_password, sql_server_database


    def sync_a_table(self, sql_cursor, machine_id, after=None):
        # <pymssql._pymssql.Cursor object at 0x7f1224203e88> 11CEQt4jMvqBscvUtnLQ8qoG 2021-12-21 02:11:56
        delta = timedelta(hours=+8)  # ！
        if after:
            after += delta
        table_name = 'm' + machine_id
        sql = ( f'SELECT FileName, FileUUD, FileStitches, BaseLineUse, ProcCounts, ProcTime, EndStitch, NodeDistance, StartTime, CreateTime FROM {table_name}'
                + (' WHERE StartTime>%(after)s' if after else '') )
        # print(sql, after)

        sql_cursor.execute(sql, dict(after=after))

        n = 0
        for row in sql_cursor:
            self.sudo().create(dict(
                MachineID = machine_id,
                FileName = row['FileName'],
                FileUUD = row['FileUUD'],
                FileStitches = row['FileStitches'],
                BaseLineUse = row['BaseLineUse'],
                ProcCounts = row['ProcCounts'],
                ProcTime = row['ProcTime'],
                EndStitch = row['EndStitch'],
                NodeDistance = row['NodeDistance'],
                StartTime = row['StartTime'] - delta,
                CreateTime = row['CreateTime'] - delta,
            ))
            n += 1

        _logger.info(f'sync {n} template_machine_record from {table_name}')


    def sync(self):
        # print('*'*80, 'sync template_machine_record')

        sql_server_host, sql_server_user, sql_server_password, sql_server_database = self.get_mssql_db_configuration()
        _logger.info(f'sync template_machine_record from SQL Server DB {sql_server_database}')

        groups = self.sudo().read_group([], fields=['MachineID','StartTime:max'], groupby=['MachineID'])
        machine_stats = {}
        for group in groups:
            # print(group)
            machine_id = group['MachineID']
            machine_stats[machine_id] = group['StartTime']

        with pymssql.connect(sql_server_host,sql_server_user,sql_server_password,sql_server_database) as conn:
            with conn.cursor(as_dict=True) as cursor:
                # cursor.execute('SELECT UUID FROM MachineInfo')
                cursor.execute('SELECT UUID FROM Record_RunTime GROUP BY UUID')
                machines = list(cursor)  # 注意 curosr 的状态！
                for machine in machines:
                    machine_id = machine['UUID']
                    self.sync_a_table(cursor, machine_id, after=machine_stats.get(machine_id))


    def check_update(self, count):
        # print('*'*80, 'check_update')
        n = self.sudo().search_count([])
        # print(count, n)
        return n != count

