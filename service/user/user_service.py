import os
import yaml
import bcrypt
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

_users_config = os.path.join(os.environ['CONFIG_DIR'], "users.yml")


@auth.verify_password
def verify_password(username, password):
    """
    Verify if the given password is valid for the given user.

    Checks against the bcrypt hashed password stored in the users config.

    Gets called internally by flask_httpauth.

    :param str username:
    :param str password:
    :return Boolean:
    """
    with open(_users_config, 'r', encoding="utf-8") as _users_file:
        _users = yaml.safe_load(_users_file)
    if username in _users:
        hashed_password = _users.get(username)['password'].encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
    return False


def get_all_users():
    """
    Returns a list of all known user names.
    """
    with open(_users_config, 'r', encoding="utf-8") as _users_file:
        _users = yaml.safe_load(_users_file)

        return list(_users.keys())