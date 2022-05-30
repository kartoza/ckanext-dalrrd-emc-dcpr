import logging
import typing

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.spatial.interfaces import ISpatialHarvester

logger = logging.getLogger(__name__)


class HarvestingPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    """Custom plugin to deal with harvesting-related customizations.

    This class exists in order to work around a bug in ckanext-spatial:

        https://github.com/ckan/ckanext-spatial/issues/277

    The mentioned bug prevents being able to have a CKAN extension plugin using both
    the `IValidators` and the `ISpatialHarvester` interfaces at the same time.

    As an alternative, we have implemented the current plugin class with the aim
    to use it strictly for customization of the harvesters (_i.e._ implement the
    ISpatialHarvester interface) while the main plugin class
    (emc_dcpr_plugin.DalrrdEmcDcprPlugin) is still handling all of the other EMC-DCPR
    customizations.

    """

    plugins.implements(ISpatialHarvester, inherit=True)

    def get_package_dict(
        self, context: typing.Dict, data_dict: typing.Dict[str, typing.Any]
    ) -> typing.Dict[str, typing.Any]:
        """Extension point required by ISpatialHarvester"""
        logger.info(f"inside get_package_dict - hey there!")
        return data_dict.get("package_dict", {})
