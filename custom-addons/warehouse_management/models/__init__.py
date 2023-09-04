# -*- coding: utf-8 -*-

from . import models

# 供应商
# from . import supplier_supplier

from . import material_code     # 物料编码（物料和面料共用）

from . import mian_fu_liao_bu_liao

from . import customer_repair
from . import warehouse_bom
from . import warehouse_bom_outbound
from . import warehouse_bom_inventory
from . import warehouse_bom_inventory_month
from . import material_list

from . import plus_material_list
from . import plus_material_enter
from . import plus_material_inventory
from . import plus_material_inventory_month
from . import plus_material_outbound

from . import production_operation_ingredients_list
from . import production_operation_ingredients_enter
from . import production_operation_ingredients_inventory
from . import production_operation_ingredients_outbound


from . import finished_product_ware
from . import finished_inventory
from . import finished_inventory_month
from . import fabric_ingredients_procurement
from . import fabric_ingredients_refund

from . import inherit_client_ware

from . import production_drop_documents

from . import outsource_order

from . import spare_fabric_storage
from . import spare_material_storage
from . import spare_fabric_inventory_month
from . import spare_material_inventory_month