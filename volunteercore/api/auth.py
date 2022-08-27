from flask import jsonify, request, url_for, g  
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask_session import Session
from flask_login import current_user, login_user, logout_user, login_required
from volunteercore import db, login_manager
from volunteercore.api import bp
from volunteercore.auth.models import User, Role
from volunteercore.api.errors import bad_request, error_response
from volunteercore.decorators import requires_roles
from time import time

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

# Defines the HTTPBasicAuth callback function password verification used
# when basic auth is used on a route function
@basic_auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return False
    g.current_user = user
    return user.verify_password(password)

# Defines the error response if HTTPBasicAuth fails
@basic_auth.error_handler
def basic_auth_error_handler():
    return error_response(400, message='username or password incorrect')

# Defines the HTTPTokenAuth callback function token verification used
# when token auth is used on a route function
@token_auth.verify_token
def verify_token(token):
    g.current_user = User.check_token(token) if token else None
    return g.current_user is not None

# Defines the error response if HTTPTokenAuth fails
@token_auth.error_handler
def token_error_handler():
    return error_response(401)

# Defines the error response if @login_required failes
@login_manager.unauthorized_handler
def unauthorized_callback():
    return error_response(401, message='please log in')

# API POST endpoint for logging in a user. Requires username:password and
# returns HTTP-Only cookie. Sets session user, current_user.
@bp.route('/api/auth/login', methods=['POST'])
@basic_auth.login_required
def login():
    if g.current_user is None:
        return error_response(401)
    login_user(g.current_user)
    return jsonify({"status":'user logged in'}), 201

# API POST endpoint for logging out a user.
@bp.route('/api/auth/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({"status":'user logged in'}), 201

# API GET endpoint returns an individual user. The users email is only
# returned when the include_email argument is pass as True.
@bp.route('/api/users/<int:id>', methods=['GET'])
@login_required
@requires_roles('Admin')
def get_user_api(id):
    include_email = request.args.get('include_email', False)
    return jsonify(User.query.get_or_404(id).to_dict(include_email))

# API GET endpoint return all users, paginated with given page and quantity
# per page.
@bp.route('/api/users', methods=['GET'])
@login_required
@requires_roles('Admin')
def get_users_api():
    include_email = request.args.get('include_email', False)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_colletion_dict(
            User.query, page, per_page, 'api.get_users_api', include_email=include_email)
    return jsonify(data)

# API GET endpoint to return the authenticated user
@bp.route('/api/users/authenticated_user', methods=['GET'])
@login_required
def get_authenticated_user_api():
    return jsonify(
        User.query.filter_by(username=current_user.username).first().to_dict(include_email=True))

# API POST endpoint to create a new user
@bp.route('/api/users/create', methods=['POST'])
def create_user_api():
    data = request.get_json() or {}
    if 'username' not in data or 'password' not in data or 'email' not in data:
        return bad_request('must include username/password/email field')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('this user already exists')
    user = User()
    user.from_dict(data)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user_api', id=user.id)
    return response

# API PUT endpoint to update a user
@bp.route('/api/users/<int:id>', methods=['PUT'])
@login_required
@requires_roles('Admin')
def update_user_api(id):
    user = User.query.get_or_404(id)
    data = request.get_json() or {}
    if 'username' in data and data['username'] != user.username and \
            User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if 'roles' in data:
        for role in data['roles']:
            if not Role.query.filter_by(name=role).first():
                return bad_request('that is not an existing role')
    user.from_dict(data)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict())

# API DELETE endpoint to delete a user
@bp.route('/api/users/<int:id>', methods=['DELETE'])
@login_required
@requires_roles('Admin')
def delete_user_api(id):
    if not User.query.filter_by(id=id).first():
        return bad_request('this user does not exist')
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return '', 204


# API GET to retreive the current version
@bp.route('/api/version',methods=['GET'])
def get_version():
    with open('.git/packed-refs','r') as fd:
        data = fd.readlines()[1]
        data = data.split(' ')[0]
    return data, 200
