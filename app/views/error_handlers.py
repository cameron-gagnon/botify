from flask import Blueprint

error_handlers = Blueprint('error_handlers', __name__, template_folder='templates')

# handles all errors
@error_handlers.app_errorhandler(Exception)
def all_errors(error):
    print(error)
    return 'An error occurred, yell at stroopC', 500
