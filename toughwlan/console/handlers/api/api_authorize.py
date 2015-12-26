#!/usr/bin/env python
#coding=utf-8

from toughlib import utils, apiutils
from toughlib.permit import permit
from toughwlan.console.handlers.api import api_base
from toughwlan.console import models

@permit.route(r"/api/authorize")
class AuthorizeHandler(api_base.ApiHandler):
    """ authorize handler"""

    def post(self):
        try:
            req_msg = self.parse_request()
            if 'username' not in req_msg:
                raise ValueError('username is empty')
        except Exception as err:
            self.render_json(msg=utils.safestr(err.message))
            return

        username = req_msg['username']
        account = self.db.query(models.ResAccount).filter_by(account_number=username)
        if not account:
            self.render_json(code=1, msg='user  {0} not exists'.format(username))

        passwd = utils.decrypt(account.password)

        result = dict(
            code=0,
            msg='success',
            username=username,
            passwd=passwd,
            input_rate=4194304,
            output_rate=4194304,
            attrs={
                "Session-Timeout"      : 3600,
                "Acct-Interim-Interval": 300
            }
        )

        sign = apiutils.make_sign(self.settings.config.system.secret, result.values())
        result['sign'] = sign
        self.render_json(**result)

