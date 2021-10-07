import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from .commands.test import test_ckan_cmd


class DalrrdEmcDcprPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IClick)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic',
            'dalrrd_emc_dcpr')

    def get_commands(self):
        return [test_ckan_cmd]
