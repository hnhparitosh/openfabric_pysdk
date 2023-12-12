# ----------------------------
# !!!  Perform GEVENT monkey patch
# ----------------------------
from gevent import monkey
monkey.patch_all()

try:
  # This is in order to be able to use a newer werkzeug version
  # without having to update to the latest flask
  # as the marketplace is still using an older socketIO client
  import werkzeug.serving as werkzeug_serving
  if not hasattr(werkzeug_serving, 'run_with_reloader'):
    import werkzeug
    import werkzeug._reloader
    werkzeug.serving.run_with_reloader = werkzeug._reloader
except:
  # Failed patching werkzeug.
  # Maybe something else is used
  pass

import pathlib
from flask import Flask as Webserver, render_template, request, session
from flask_cors import CORS
from requests import get, post, patch, delete, Request, Response

webserver = Webserver(__name__, template_folder=f"{pathlib.Path(__file__).parent}/../../view")
CORS(webserver)
