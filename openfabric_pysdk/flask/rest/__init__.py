# Services
from flask_restful import Api as WebserverRestAPI
from flask_apispec import FlaskApiSpec as WebserverRestDoc

# Class definition
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import doc, marshal_with, use_kwargs

# Swagger
from apispec import APISpec as WebserverSwaggerSpec
from apispec.ext.marshmallow import MarshmallowPlugin as SwaggerMarshmallowPlugin
