from typing import Any, Dict

#######################################################
#  Schema util
#######################################################
class SchemaUtil:

    @staticmethod
    def create(instance: Any, data: Dict[Any, Any]):
        for key in data:
            instance.__setattr__(key, data[key])
        return instance
