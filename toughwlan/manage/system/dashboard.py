#!/usr/bin/env python
# coding:utf-8
import os
import subprocess
import os.path
import tornado.web
from toughwlan.manage.base import BaseHandler, MenuSys
from toughlib.permit import permit


##############################################################################
# basic
##############################################################################

class ToughError(Exception):
    def __init__(self, message):
        self.message = message


def run_command(command, raise_error_on_fail=False, shell=True, env=None):
    _result = dict(code=0)
    run_env = os.environ.copy()
    if env: run_env.update(env)
    proc = subprocess.Popen(command, shell=shell,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            env=run_env)
    stdout, stderr = proc.communicate('through stdin to stdout')
    result = proc.returncode, stdout, stderr
    if proc.returncode > 0 and raise_error_on_fail:
        error_string = "* Could not run command (return code= %s)\n" % proc.returncode
        error_string += "* Error was:\n%s\n" % (stderr.strip())
        error_string += "* Command was:\n%s\n" % command
        error_string += "* Output was:\n%s\n" % (stdout.strip())
        if proc.returncode == 127:  # File not found, lets print path
            path = os.getenv("PATH")
            error_string += "Check if y/our path is correct: %s" % path
        raise ToughError(error_string)
    else:
        return result


def warp_html(code, value):
    _value = value.replace("\n", "<br>")
    _value = _value.replace("RUNNING", "<strong><font color=green>RUNNING</font></strong>")
    _value = _value.replace("STARTING", "<strong><font color='#CC9900'>STARTING</font></strong>")
    _value = _value.replace("FATAL", "<strong><font color=red>FATAL</font></strong>")
    if code > 0:
        _value = '<font color="#CC0000">%s</font>' % _value
    return _value


def execute(cmd):
    try:
        rcode, stdout, stderr = run_command(cmd, True)
        return dict(value=warp_html(rcode, (stdout or stderr)))
    except ToughError, err:
        import traceback
        traceback.print_exc()
        return dict(value=warp_html(1, err.message))


##############################################################################
# web handler
##############################################################################

@permit.route(r"/dashboard", u"控制面板", MenuSys, order=1.0000, is_menu=True, is_open=False)
class DashboardHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        self.render("index.html", config=self.settings['config'])

@permit.route(r"/dashboard/initdb", u"初始化数据库", MenuSys, order=1.0001, is_menu=False)
class InitdbHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        return self.render_json(**execute("/opt/toughwlan/toughctl --initdb"))


@permit.route(r"/dashboard/restart", u"重启服务", MenuSys, order=1.0004, is_menu=False)
class RestartHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        return self.render_json(**execute("supervisorctl restart all && supervisorctl status all"))


@permit.route(r"/dashboard/update", u"更新系统状态", MenuSys, order=1.0002, is_menu=False)
class UpdateHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        return self.render_json(**execute("supervisorctl status all"))


@permit.route(r"/dashboard/upgrade", u"升级系统版本", MenuSys, order=1.0003, is_menu=False)
class UpgradeHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        release = self.get_argument("release")
        cmd1 = "cd /opt/toughwlan"
        cmd2 = "git checkout %s git pull origin %s " % (release, release)
        cmd3 = "supervisorctl restart all"
        return self.render_json(**execute("%s && %s && %s" % (cmd1, cmd2, cmd3)))






