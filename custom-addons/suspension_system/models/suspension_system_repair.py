from odoo import api, fields, models
from . import mssaql_class
import itertools

class SuspensionSystemRepair(models.Model):
    _name = 'suspension_system_repair'
    _description = '吊挂修复信息'


    date = fields.Date(string="日期")
    order_number = fields.Many2one('sale_pro.sale_pro', string='订单号（对象）')
    order_number_show = fields.Char(string="订单号")
    style_number = fields.Many2one('ib.detail', string='款号（对象）')
    style_number_show = fields.Char(string="款号")
    product_size = fields.Many2one("fsn_size", string="尺码（对象）")
    product_size_show = fields.Char(string="尺码")
    number = fields.Integer(string='件数')


    def get_repair_info(self, today):

        dg_db_host = self.env.ref('fsn_setting.dg_db_host').value
        dg_db_user = self.env.ref('fsn_setting.dg_db_user').value
        dg_db_password = self.env.ref('fsn_setting.dg_db_password').value
        dg_db_database = self.env.ref('fsn_setting.dg_db_database').value

        dg_sqlserver = mssaql_class.MSSQL(host=dg_db_host, user=dg_db_user, pwd=dg_db_password, db=dg_db_database)

        sql = f"select * from tWorkHis where dDate = '{today}' and InsOrder > 1;"

        reslist = dg_sqlserver.ExecQuery(sql)

        reslist = [list(i) for i in reslist]

        for i in reslist:
            if len(i[8]) > 7:
                i[8] = i[8][0:7]

        reslist.sort(key=lambda x: (x[8], x[9], x[10]), reverse=False)      # 排序
        for (order_number, style_number, product_size), objs in itertools.groupby(reslist, key=lambda x: (x[8], x[9], x[10])):     # 分组


            obj = self.search([
                ("date", "=", today),
                ("order_number_show", "=", order_number),
                ("style_number_show", "=", style_number),
                ("product_size_show", "=", product_size),
            ])

            if obj:
                obj.number = len(list(objs))
            else:
                self.create({
                    "date": today,
                    "order_number": self.env['sale_pro.sale_pro'].search([("order_number", "=", order_number)]).id,
                    "order_number_show": order_number,
                    "style_number": self.env['ib.detail'].search([("style_number", "=", style_number)]).id,
                    "style_number_show": style_number,
                    "product_size": self.env['fsn_size'].search([("name", "=", product_size)]).id,
                    "product_size_show": product_size,
                    "number": len(list(objs))
                })





