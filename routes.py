from flask import jsonify, request
from flask_jwt_extended import create_access_token
from flask import jsonify, request, make_response
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from app import app, db
from models import User
from flask.views import MethodView

#----------------------------------------------Login-Logout----------------------------------------------
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(name=data['name']).first()
    if user and user.age == data['age'] and user.city == data['city']:
        access_token = create_access_token(identity=user.id)
        response = make_response(jsonify({'message': 'Logged in successfully'}), 200)
        response.set_cookie('access_token', access_token, httponly=True)
        return response
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/logout', methods=['POST'])
@jwt_required(optional=True)  # Allow unauthenticated access for logout
def logout():
    response = make_response(jsonify({'message': 'Logged out successfully'}), 200)
    response.delete_cookie('access_token')
    return response

#---------------------------------------------------------------------------------------------------------
class UsersView(MethodView):
    decorators = [jwt_required()]

    def get(self, user_id=None):
        get_jwt_identity()
        if user_id is None:
            users = User.query.filter_by(is_active = True).order_by(User.id.desc())
            user_list = [{'id': user.id, 'name': user.name, 'age': user.age, 'city': user.city, 'is_active': user.is_active} for user in users]
            return jsonify(user_list)
        else:
            user = User.query.get(user_id)
            users = User.query.filter_by(id = user.id, is_active = True).all()
            print(users,'-----')
            if user:
                user_data =  [{'id': user.id, 'name': user.name, 'age': user.age, 'city': user.city, 'is_active': user.is_active} for user in users]
                return jsonify(user_data)
            return jsonify({'error': 'User not found'}), 404

    def post(self):
        # get_jwt_identity()
        data = request.json
        new_user = User(name=data['name'], age=data['age'], city=data['city'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201

    def put(self, user_id):
        get_jwt_identity()
        user = User.query.get(user_id)
        if user:
            data = request.json
            user.name = data['name']
            user.age = data['age']
            user.city = data['city']
            db.session.commit()
            return jsonify({'message': 'User updated successfully'})
        return jsonify({'error': 'User not found'}), 404

    def delete(self, user_id):
        get_jwt_identity()
        user = User.query.get(user_id)
        if user:
            # db.session.delete(user)
            user.is_active = False
            db.session.commit()
            return jsonify({'message': 'User deleted successfully'})
        return jsonify({'error': 'User not found'}), 404

users_view = UsersView.as_view('users_view')
app.add_url_rule('/users', view_func=users_view, methods=['GET', 'POST'])
app.add_url_rule('/users/<int:user_id>', view_func=users_view, methods=['GET', 'PUT', 'DELETE'])