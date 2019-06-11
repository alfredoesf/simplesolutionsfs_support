# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _

class ReportAccountFinancialReport(models.Model):
    _inherit = "account.financial.html.report"

    @api.multi
    def _get_lines(self, options, line_id=None):
        res = super(ReportAccountFinancialReport, self)._get_lines(options, line_id)
        new_res = []
        list_of_accounts = []
        last = False
        for r in res:
            if r.get('caret_options', False) and r.get(
                    'caret_options') == 'account.account':
                list_of_accounts.append(r)
            else:
                list_of_dict = []
                nodes_sorted = []
                if len(list_of_accounts) > 0:
                    list_of_dict = self.get_dict(list_of_accounts, last)
                    nodes_sorted = self.rebuild_tree(list_of_dict)
                    for node in nodes_sorted:
                        new_res.append(node)
                new_res.append(r)
                list_of_accounts = []
                last = r
        return new_res

    def rebuild_tree(self, list_of_dict):
        list_of_dict_copy = list_of_dict.copy()
        nodes_root = []
        final_list = []
        for l in list_of_dict:
            if not l.get('pa_id', False):
                nodes_root.append(l)
                list_of_dict_copy.remove(l)

        nodes_root = sorted(nodes_root, key=lambda k: k['id'])
        nodes_root.extend(list_of_dict_copy)

        def recursive_childs(root, nodes_root):
            if not self.exist_node(root, final_list):
                final_list.append(root)

            childs = self.get_childs(root, nodes_root)
            ordered_childs = sorted(childs, key=lambda k: k['id'])
            if len(childs) == 0:
                nodes_root.remove(root)
            else:
                recursive_childs(ordered_childs[0], nodes_root)

        while len(nodes_root) > 0:
            root = nodes_root[0]
            recursive_childs(root, nodes_root)

        return final_list

    def exist_node(self, root, final_list):
        for ls in final_list:
            if ls.get('id') == root.get('id'):
                return True
        return False

    def get_childs(self, root, list_of_dict_copy):
        list_childs = []
        for ls in list_of_dict_copy:
            if ls.get('pa_id') == root.get('id'):
                list_childs.append(ls)
        return list_childs

    def get_dict(self, list_of_accounts, last):
        """
        Function to calculate the hierarchical structure to show.
        :param list_of_accounts: list of dict with records to print
        :param last: dict with the last parent
        :return:
        """
        list_of_dict = []
        for account in list_of_accounts:
            parents_ids = self.get_recursive_parents(account, last)
            account_id = account.get('id', False)
            account_obj = self.env['account.account'].browse(account_id)
            pa_id = False
            if len(list_of_dict) == 0:
                list_of_dict = parents_ids
                account['class'] = 'o_js_account_report_inner_row o_account_reports_level_extended%d' \
                               % (account_obj.level * 2 if account_obj.level > 0 else 1)
                if parents_ids:
                    pa_id = parents_ids[len(parents_ids) - 1].get('id')
                account['pa_id'] = pa_id
                list_of_dict.append(account)
            else:
                index = len(list_of_dict)

                for pas in parents_ids:
                    count_flag = len(list_of_dict)
                    for lis in list_of_dict:
                        if pas.get('id') == lis.get('id'):
                            count_flag -= 1
                            pa_id = pas.get('id')
                            if len(account.get('columns')) == 1:
                                balance = lis.get('columns')[0]['no_format_name']
                                balance = balance + pas.get('columns')[0]['no_format_name']
                                columns = [
                                    {
                                        'name': self.format_value(balance),
                                        'no_format_name': balance
                                    }
                                ]
                                lis['columns'] = columns
                            else:
                                count = len(account.get('columns'))
                                i = 0
                                columns = []
                                while i < count:
                                    if account.get('columns')[i].get(
                                            'no_format_name', False):
                                        name = lis.get('columns')[i]['no_format_name']
                                        name = name + pas.get('columns')[i]['no_format_name']
                                        try:
                                            format_value = self.format_value(
                                                name)
                                        except Exception as e:
                                            format_value = self.format_value(
                                                0.00)
                                        val = {
                                            'name': format_value,
                                            'no_format_name': name
                                        }
                                    else:
                                        name = account.get('columns')[i].get(
                                            'name', False)
                                        if not name:
                                            name = 'n/a'
                                        val = {
                                            'name': name,
                                        }
                                    columns.append(val)
                                    i += 1
                            break
                    if count_flag == len(list_of_dict):
                        list_of_dict.append(pas)

                ix = 0
                val = False
                for ls in list_of_dict:
                    ix += 1
                    if pa_id and ls.get('pa_id') == pa_id:
                      val = ix
                if val:
                    index = val

                account['class'] = 'o_js_account_report_inner_row o_account_reports_level_extended%d' \
                                   % (account_obj.level * 2 if account_obj.level > 0 else 1)
                account['pa_id'] = parents_ids[len(parents_ids) - 1].get('id') if parents_ids else False
                list_of_dict.insert(index, account)
        return list_of_dict

    def get_recursive_parents(self, account, last):
        """
        Function to get the parents of the account
        :param account: dict with data of account
        :param last: dict with the last parent
        :return: list of dict with the parents of account
        """
        account_id = account.get('id', False)
        account_obj = self.env['account.account'].browse(account_id)
        parents = []
        while account_obj.parent_id:
            if len(account.get('columns')) == 1:
                if account.get('columns')[0].get('no_format_name', False):
                    name = account.get('columns')[0]['no_format_name']
                else:
                    name = account.get('columns')[0]['name']
                columns = [{
                        'name': self.format_value(name),
                        'no_format_name': name
                        }
                ]
            else:
                count = len(account.get('columns'))
                index = 0
                columns = []
                while index < count:
                    if account.get('columns')[index].get(
                            'no_format_name', False):
                        if account.get('columns')[index].get('no_format_name', False):
                            name = account.get('columns')[index]['no_format_name']
                        else:
                            name = account.get('columns')[index]['name']
                        try:
                            format_value = self.format_value(name)
                        except Exception as e:
                            format_value = self.format_value(0.00)
                        val = {
                            'name': format_value,
                            'no_format_name': name
                        }
                    else:
                        name = account.get('columns')[index].get(
                            'name', False)
                        if not name:
                            name = 'n/a'
                        val = {
                            'name': name,
                        }

                    columns.append(val)
                    index += 1

            parent = {
                'id': account_obj.parent_id.id,
                'name': account_obj.parent_id.display_name,
                'class': 'o_account_reports_domain_total o_account_reports_totals_below_sections  o_js_account_report_inner_row',
                'columns': columns,
                'level': (account_obj.parent_id.level * 2) + 3,
                'parent_id': last.get('id'),
                'unfoldable': False,
                'unfolded': False,
                'page_break': False,
                'pa_id': account_obj.parent_id.parent_id.id if
                account_obj.parent_id.parent_id else False
            }
            parents.append(parent)
            account_obj = account_obj.parent_id
        parents.reverse()
        return parents