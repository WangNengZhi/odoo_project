# $ ./odoo-bin -c odoo.conf --test-tags dev_test
from odoo.tests import common, tagged

@tagged('-standard', 'dev_test')
class TestModelA(common.TransactionCase):
    def test_stats(self):
        res = self.env['hard_working_workers_of_year'].stats((2021,8), (2022,7), 15, 2)

        print('#'*20, len(res))
        for x in res:
            print('*'*20, x.id, x.name)

