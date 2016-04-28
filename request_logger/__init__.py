from flask import Flask

app = Flask(__name__)

from request_logger import views
