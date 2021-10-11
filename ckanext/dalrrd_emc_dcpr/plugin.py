import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from .commands.test import test_ckan_cmd


class DalrrdEmcDcprPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.IDatasetForm)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("fanstatic", "dalrrd_emc_dcpr")

    def get_commands(self):
        return [test_ckan_cmd]

    # IDatasetForm

    def _admins_only_create(self, value, context):
        user_name = context.get('user')
        private = value
        package = context.get('package')

        members = toolkit.get_action('member_list')(
            data_dict={'id': package.owner_org, 'object_type': 'user'})

        admin_member_ids = [member_tuple[0] for member_tuple in members if member_tuple[2] == 'Admin']

        convert_user_name_or_id_to_id = toolkit.get_converter(
            'convert_user_name_or_id_to_id')
        user_id = convert_user_name_or_id_to_id(user_name, context)

        if (not private) and (user_id not in admin_member_ids):
            raise toolkit.Invalid('Only Admin users may set datasets as public')
        else:
            return value

    def _admins_only_update(self, value, context):

        package = context.get('package')
        user_name = context.get('user')
        private = value

        members = toolkit.get_action('member_list')(
            data_dict={'id': package.owner_org, 'object_type': 'user'})

        admin_member_ids = [member_tuple[0] for member_tuple in members if member_tuple[2] == 'Admin']

        convert_user_name_or_id_to_id = toolkit.get_converter(
            'convert_user_name_or_id_to_id')
        user_id = convert_user_name_or_id_to_id(user_name, context)
        if (not private) and (user_id not in admin_member_ids) and (private != package.private):
            raise toolkit.Invalid('Only Admin users may set datasets as public')
        else:
            return value

    def create_package_schema(self):
        schema = super(DalrrdEmcDcprPlugin, self).create_package_schema()

        schema.update({
            'private': schema['private'] + [self._admins_only_create]
        })
        return schema

    def update_package_schema(self):
        schema = super(DalrrdEmcDcprPlugin, self).update_package_schema()

        schema.update({
            'private': schema['private'] + [self._admins_only_update]
        })
        return schema

    def is_fallback(self):
        return True

    def package_types(self):
        return []
