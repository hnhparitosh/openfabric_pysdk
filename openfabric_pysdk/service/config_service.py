from typing import Dict, List, Union

from openfabric_pysdk.app import App
from openfabric_pysdk.loader import ConfigClass, ConfigSchema
from openfabric_pysdk.transport.schema import UserId


#######################################################
#  Config service
#######################################################
class ConfigService:

    # ------------------------------------------------------------------------
    @staticmethod
    def read(app: App, uidc: UserId) -> ConfigClass:
        state_config = app.get_state_config()
        config = state_config.get(uidc.uid)
        if config is False:
            return dict()
        return config

    # ------------------------------------------------------------------------
    @staticmethod
    def write(app: App, uidc: UserId, config: Union[ConfigClass, List[ConfigClass]]) -> Dict[str, ConfigClass]:
        if ConfigSchema().many is True and not isinstance(config, list):
            config = [config]
        else:
            config = config[0] if type(config) == list else config
        # Store
        state_config = app.get_state_config()
        state_config.set(uidc.uid, ConfigSchema().dump(config))
        # Apply configuration
        ConfigService.apply(app)

        return config

    # ------------------------------------------------------------------------
    @staticmethod
    def apply(app: App):
        all_items = ConfigService.read_all(app)
        app.config_callback_function(all_items)

    # ------------------------------------------------------------------------
    @staticmethod
    def read_all(app: App) -> Dict[str, ConfigClass]:
        # Reload form config file
        state_config = app.get_state_config()
        items = state_config.all().items()
        return dict(map(lambda kv: (kv[0], ConfigSchema().load(kv[1])), items))
