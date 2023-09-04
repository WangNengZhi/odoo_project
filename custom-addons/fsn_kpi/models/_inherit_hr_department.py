from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrDepartment(models.Model):
    _inherit = 'hr.department'


    is_kpi = fields.Boolean(string="是否kpi")

    kpi_template_menu_id = fields.Many2one('ir.ui.menu', string='KPI模板菜单')
    kpi_menu_id = fields.Many2one('ir.ui.menu', string='KPI菜单')


    # 创建kpi菜单和群组
    def create_kpi_content(self, fsn_kpi_menu_obj, fsn_kpi_model, fsn_kpi_name):

        # 创建动作
        fsn_kpi_action_obj = self.env["ir.actions.act_window"].sudo().create({
            "name": self.name + fsn_kpi_name,
            "res_model": fsn_kpi_model,
            "view_mode": "tree,form",
            "domain": f"[('department_id', '=', {self.id})]",
            "context": "{'default_department_id': %s}" % self.id,
        })
        # 创建菜单
        kpi_menu_obj = self.env["ir.ui.menu"].sudo().create({
            "name": self.name + fsn_kpi_name,
            "parent_id": fsn_kpi_menu_obj.id,
            "action": 'ir.actions.act_window,%s' % fsn_kpi_action_obj.id,
            "sequence": self.id * 10,
        })

        return kpi_menu_obj.id


    # 创建kpi群组
    def create_groups(self):

        # 获取kpi组分类
        fsn_kpi_category_obj = self.env.ref('fsn_kpi.fsn_kpi_category')
        # 获取父组
        fsn_kpi_father_group_obj = self.env.ref('fsn_kpi.fsn_kpi_group_00')

        # 创建群组
        res_groups_obj = self.env["res.groups"].sudo().create({
            "name":self.name,
            "category_id": fsn_kpi_category_obj.id,
            "implied_ids": [(4, fsn_kpi_father_group_obj.id)]
        })
        # kpi_menu_obj.groups_id = [(4, res_groups_obj.id)]
        return res_groups_obj.id


    # 生成kpi内容
    def generate_kpi(self):
        
        # 先检查是否已经又了kpi资源
        if self.kpi_menu_id or self.kpi_template_menu_id:
            raise ValidationError(f"已经存在该部门的KPI资源了，无需重复生成。")
        else:
            # 获取kpi父菜单
            fsn_kpi_menu_obj = self.env.ref('fsn_kpi.fsn_kpi_menu')
            # kpi模型名
            fsn_kpi_model = "fsn_kpi"
            # 名称
            fsn_kpi_name = "KPI"


            # 获取kpi模板父菜单
            kpi_setting_menu_obj = self.env.ref('fsn_kpi.kpi_setting_menu')
            # kpi模板模型名
            fsn_kpi_template_model = "fsn_kpi_template"
            # 名称
            fsn_kpi_template_name = "KPI模板"

            # 创建kpi菜单和动作
            self.kpi_menu_id = self.create_kpi_content(fsn_kpi_menu_obj, fsn_kpi_model, fsn_kpi_name)
            # 创建kpi模板菜单和动作
            self.kpi_template_menu_id = self.create_kpi_content(kpi_setting_menu_obj, fsn_kpi_template_model, fsn_kpi_template_name)
            # 创建kpi群组
            fsn_kpi_group_id = self.create_groups()
            self.kpi_menu_id.groups_id = [(4, fsn_kpi_group_id)]
            self.kpi_template_menu_id.groups_id = [(4, fsn_kpi_group_id)]

    

    # 删除kpi菜单和群组
    def delete_kpi_content(self, obj):
        # 删除动作
        obj.action.sudo().unlink()
        # 删除群组
        obj.groups_id.sudo().unlink()
        # 删除菜单
        obj.sudo().unlink()
        


    # 删除kpi内容
    def delete_kpi(self):

        # 删除kpi菜单和群组
        self.delete_kpi_content(self.kpi_menu_id)
        # 删除kpi模板菜单和群组
        self.delete_kpi_content(self.kpi_template_menu_id)

        


