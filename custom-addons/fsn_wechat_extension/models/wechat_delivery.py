from odoo import models, fields, api


class WechatDelivery(models.Model):
    _name = 'wechat.delivery'
    _description = '中查交货'

    date = fields.Date(string="交货日期", required=True)
    check_in_name = fields.Many2one('hr.employee', string='中查姓名')

    # group = fields.Many2one("fsn_staff_team", string='组别')
    # order_number = fields.Many2one("sale_pro.sale_pro", string='订单号')
    # style_number = fields.Many2one("ib.detail", string='款号')

    group = fields.Many2one('check_position_settings', string='组别')
    order_number = fields.Char(string='订单号')
    style_number = fields.Char(string='款号')

    large_cargo_inspection_number = fields.Integer(string='大货查货数')
    number_of_bulk_repairs = fields.Integer(string='大货返修数')
    number_of_bulk_deliveries = fields.Integer(string='大货交货数')
    number_of_secondary_inspections = fields.Integer(string='二次查货返修数')
    number_of_secondary_repairs = fields.Integer(string='二次返修数')
    number_of_second_repair_deliveries = fields.Integer(string='二次返修交货数')
    problems = fields.Char(string='问题点')
    question_points = fields.Integer(string='问题点数')
    rework_type = fields.Char(string='返修类型')
    parking_space_name = fields.Many2one("hr.employee", string='车位姓名')

    status = fields.Selection([
        ('待审批', '待审批'),
        ('审批通过', '审批通过'),
        ('拒绝', '拒绝')
    ], string='状态', default='待审批', compute="set_status", store=True)


    @api.depends("wechat_delivery_line_ids", "wechat_delivery_line_ids.status")
    def set_status(self):
        for record in self:
            if all([i.status == '审批通过' for i in record.wechat_delivery_line_ids]):
                if record.status != "审批通过":
                    record.status = "审批通过"
                    # existing_record = self.env['invest.invest'].sudo().search([('date', '=', record.date)])
                    # if not existing_record:
                        # 写入数据库

                    # 获取订单号
                    order_number = self.env['sale_pro.sale_pro'].search([('order_number', '=', record.order_number)]).id
                    # 获取款号
                    style_number = self.env['ib.detail'].search([('style_number', '=', record.style_number)]).id
                    # print(order_number, style_number)
                    data = {
                        'date': record.date,
                        'group': record.group.group,
                        'invest': record.check_in_name.name,
                        'order_number': order_number,
                        'style_number': style_number,
                        'check_the_quantity': record.large_cargo_inspection_number,
                        'repairs_number': record.number_of_bulk_repairs,
                        'quantity_of_delivery': record.number_of_bulk_deliveries,
                        'group_secondary_check_number': record.number_of_secondary_inspections,
                        'group_secondary_repair_number': record.number_of_secondary_repairs,
                        'group_secondary_delivery_number': record.number_of_second_repair_deliveries,
                        'problems': record.problems,
                        'problem_points_number': record.question_points,
                        'repair_type': record.rework_type,
                        'comment': record.parking_space_name.name
                    }
                    self.env['invest.invest'].sudo().create(data)

            elif any([i.status == '拒绝' for i in record.wechat_delivery_line_ids]):
                record.status = "拒绝"



    def set_wechat_delivery_line(self):
        approval_process_config_objs = self.env['approval_process_config'].sudo().search([("type", "=", "中查交货")])
        lines = []
        for i in approval_process_config_objs.approval_process_config_line_ids:
            line = {
                "sequence": i.sequence,
                "emp_id": i.emp_id,
            }
            lines.append((0, 0, line))

        return lines

    wechat_delivery_line_ids = fields.One2many("wechat_delivery_line", "wechat_delivery_id", string="中查交货审批进度明细", default=set_wechat_delivery_line)


class WechatDeliveryLine(models.Model):
    _name = 'wechat_delivery_line'
    _description = '中查交货审批进度明细'


    wechat_delivery_id = fields.Many2one("wechat.delivery", string="中查交货", ondelete="cascade")
    sequence = fields.Integer(string="序号")
    emp_id = fields.Many2one('hr.employee', string='审批人')
    status = fields.Selection([
        ('待审批', '待审批'),
        ('审批通过', '审批通过'),
        ('拒绝', '拒绝')
    ], string='状态', default='待审批')

