#!/usr/bin/env python
# coding:utf-8
import cyclone.web
from toughwlan import models
from toughwlan.admin.base import BaseHandler, MenuSys
from toughlib.permit import permit

@permit.route(r"/operate/log", u'操作日志查询', MenuSys, order=4.0000, is_menu=True)
class OpsListHandler(BaseHandler):
    @cyclone.web.authenticated
    def get(self):
        self.post()

    @cyclone.web.authenticated
    def post(self):
        opr_name = self.get_argument('opr_name', "")
        query_begin_time = self.get_argument('query_begin_time', "")
        query_end_time = self.get_argument('query_end_time', "")
        keyword = self.get_argument('keyword', "")
        _query = self.db.query(models.TrwOperateLog)
        if opr_name:
            _query = _query.filter(models.TrwOperateLog.operator_name==opr_name)
        if keyword:
            _query = _query.filter(models.TrwOperateLog.operate_desc.like("%"+keyword+"%"))
        if query_begin_time:
            _query = _query.filter(models.TrwOperateLog.operate_time >= query_begin_time+' 00:00:00')
        if query_end_time:
            _query = _query.filter(models.TrwOperateLog.operate_time <= query_end_time+' 23:59:59')

        return self.render('operate_log_list.html',page_data=self.get_page_data(_query),**self.get_params())






