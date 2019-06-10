import traceback
from app.errors import bp as error_bp

# handles all errors
@error_bp.app_errorhandler(Exception)
def all_errors(error):
    print(traceback.format_exc())
    return 'An error occurred, yell at stroopC', 500
