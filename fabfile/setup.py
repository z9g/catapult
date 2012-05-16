import os

from fabric.api import settings, sudo, hide, abort, run
from fabric.tasks import execute

from state import myenv
from ops import mine, is_owner, ProjTask, path_exists, is_python_module, symlink_python_module
import schema


class basic_setup(ProjTask):

    def work(self):
        home = myenv.home
        self.make_workspace(home)
        schema.Cap(home).build()

    def make_workspace(self, home):
        if path_exists(home):
            if not is_owner(home):
                abort('workspace already exists and does not belong to you, \
make sure you want to reinstall the project:%s' % home)
        else:
            with settings(hide('warnings'), warn_only=True):
                if not sudo('mkdir %s' % home).failed:
                    sudo('chown %s %s' % (myenv.owner, home))



class setup(basic_setup):

    def work(self, ver=None, *args, **kw):
        self.pre()
        super(setup, self).work()
        self.post()
        if ver:
            execute('deploy', myenv.name, ver, *args, **kw)
            self.link_path()

    def pre(self):
        if 'pre_setup' in myenv:
            for cmd in myenv.pre_setup:
                run(cmd)

    def post(self):
        if 'post_setup' in myenv:
            for cmd in myenv.post_setup:
                run(cmd)

    def link_path(self):
        for path in myenv.link_py_modules:
            if not is_python_module(path):
                abort("not a python module: %s" % path)

        for path in myenv.link_py_modules:
            symlink_python_module(path)
