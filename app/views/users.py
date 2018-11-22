# users.py
"""File contains routes for user end point"""

import re
from functools import wraps

from flask import (
    Blueprint,
    jsonify,
    request,
    json
)
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    verify_jwt_in_request,
    jwt_required
)

from app.models.user import User

users_bp = Blueprint('users_bp', __name__, url_prefix='/api/v2')

user_obj = User()


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()['user_id']
        user_obj.connect.cursor.execute("SELECT is_admin FROM users where user_id={}".format(user_id))
        is_admin = user_obj.connect.cursor.fetchone()

        if is_admin["is_admin"]:
            return func(*args, **kwargs)
        return jsonify({"message": "Unauthorized Access"}), 401

    return wrapper


def non_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()['user_id']
        user_obj.connect.cursor.execute("SELECT is_admin FROM users where user_id={}".format(user_id))
        is_admin = user_obj.connect.cursor.fetchone()

        if not is_admin["is_admin"]:
            return func(*args, **kwargs)
        return jsonify({"message": "Unauthorized Access"}), 401

    return wrapper


@users_bp.route('/auth/register', methods=['POST'])
def register():
    """Expects Parameters:
            username(type - string)
            first_name(type - string)
            last_name(type - string)
            email(type - string)# NOTE:
            password(type - string)
    """
    data = request.data
    new_user = json.loads(data)

    # empty_fields = []

    # Traverse through the new_user input data
    for key, value in new_user.items():
        # check if field is empty
        if not value:
            return jsonify({'Message': "{} cannot be empty".format(key)}), 400

    if not re.match('[^@]+@[^@]+\.[^@]+', new_user['email']):
        return jsonify({'Message': "Invalid email"}), 400

    # validate email - to be worked on
    # if not validate_email(new_user['email']):
    #     return jsonify({"Message": "Please provide a valid email"}), 400

    # Submit valid data
    return User().sign_up(username=new_user['username'],
                          firstname=new_user['firstname'],
                          lastname=new_user['lastname'],
                          email=new_user['email'],
                          password=new_user['password'],
                          is_admin=new_user['is_admin']
                          )


@users_bp.route('/auth/login', methods=['POST'])
def login():
    """Expects Parameters:
            username(type - string)
            password(type - string)
    """

    data = request.data
    credentials = json.loads(data)

    # Traverse through the new_user input data
    for key, value in credentials.items():
        # check if field is empty
        if not value:
            return jsonify({'Message': "{} cannot be empty".format(key)}), 400

    # Submit valid data
    verify_user = user_obj.login_user(username=credentials['username'], password=credentials['password'])
    if verify_user['status'] == 'success':
        # create access token
        payload = {'user_id': verify_user['user_id']}

        access_token = create_access_token(identity=payload)

        return jsonify({"access_token": access_token}), 200
    # wrong user name or password
    return jsonify({"message": "Invalid credentials"}), 400


@users_bp.route('/<userId>/parcels', methods=['GET'])
@jwt_required
def get_a_parcel_by_userId(userId):
    """Fetch all parcel delivery
    orders by a specific user """

    # cast parcelId to int
    try:

        userId = int(userId)

    except ValueError:
        # userId is not a number
        # Therefore cannot be cast to an integer

        return jsonify({"mesage": "Bad Request"}), 400

    return user_obj.get_all_parcels_for_a_specific_user(userId)
