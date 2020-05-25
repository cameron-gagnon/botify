import app

import traceback
from app.helpers.errors import bp as error_bp

# handles all errors
@error_bp.app_errorhandler(Exception)
def all_errors(error):
    with open('errors.log', 'a') as ef:
        ef.write(traceback.format_exc())
        ef.write("="*100)
        ef.write("\n\n")
    return 'An error occurred, yell at stroopC', 500
