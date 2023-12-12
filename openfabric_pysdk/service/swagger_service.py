import logging

from openfabric_pysdk.flask import SwaggerMarshmallowPlugin, Webserver, WebserverSwaggerSpec
from openfabric_pysdk.transport import ResourceDescriptor


#######################################################
#  Swagger service
#######################################################
class SwaggerService:

    # ------------------------------------------------------------------------
    @staticmethod
    def install(descriptor: ResourceDescriptor, webserver: Webserver):
        logging.info(f"Openfabric - install Specs REST endpoints on {descriptor.endpoint}")
        manifest = descriptor.app.get_manifest()
        specs = {
            'APISPEC_SPEC': WebserverSwaggerSpec(
                title="App " + manifest.get('name'),
                version=manifest.get('version'),
                plugins=[SwaggerMarshmallowPlugin()],
                openapi_version='2.0.0',
                info=dict(
                    termsOfService='https://openfabric.ai/terms/',
                    contact=dict(
                        name=manifest.get('organization'),
                        url="https://openfabric.ai"
                    ),
                    description=manifest.get('description')),
            ),
            'APISPEC_SWAGGER_URL': f'/{descriptor.endpoint}/',  # URI to access API Doc JSON
            'APISPEC_SWAGGER_UI_URL': f'/{descriptor.endpoint}-ui/'  # URI to access UI of API Doc
        }
        webserver.config.update(specs)
