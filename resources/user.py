from datetime import timedelta

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required,
)
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import UserModel
from schemas import UserSchema, LoginSchema, UpdateUserSchema
from blocklist import BLOCKLIST


blp = Blueprint("Users", "users", description="Operations on users")

@blp.route("/register")
class UserRegister(MethodView):
    @jwt_required()
    @blp.arguments(UserSchema)
    def post(self, user_data):
        """Add user."""
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409, message="A user with that username already exists.")

        user = UserModel(
            username = user_data["username"],
            password = pbkdf2_sha256.hash(user_data["password"]),
            role = user_data["role"],
            fullname = user_data["fullname"],
            designation = user_data["designation"],
            approver = user_data["approver"]
        )
        db.session.add(user)
        db.session.commit()

        return {"message": "User created successfully."}, 201


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(LoginSchema)
    def post(self, user_data):
        """Login user."""
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token_expires = timedelta(minutes=30)
            access_token = create_access_token(identity=user.username, fresh=True, expires_delta=access_token_expires)
            refresh_token_expires = timedelta(minutes=120)
            refresh_token = create_refresh_token(user.username, expires_delta=refresh_token_expires)
            user_serialized = UserSchema().dump(user)
            return {"access_token": access_token, "refresh_token": refresh_token, "user":user_serialized}, 200

        abort(401, message="Invalid credentials.")


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        """Logout user."""
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200


@blp.route("/user/<int:user_id>")
class User(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self, user_id):
        """Fetch user."""
        user = UserModel.query.get_or_404(user_id)
        return user

    @jwt_required()
    def delete(self, user_id):
        """Delete user."""
        user = UserModel.query.get_or_404(user_id)
        try:
            db.session.delete(user)
            db.session.commit()
        except SQLAlchemyError as err:
            abort(500, message="User cannot be delete. There maybe active tickets.")

        return {"message": "User deleted."}, 200

    @jwt_required()
    @blp.arguments(UpdateUserSchema)
    @blp.response(200, UserSchema)
    def put(self, user_data, user_id):
        """
        Update the user details. Requires JWT.
        """
        user = UserModel.query.get_or_404(user_id)

        # Update user fields
        user.username = user_data["username"]
        if "password" in user_data and user_data["password"] != '':
            user.password = pbkdf2_sha256.hash(user_data["password"])
        if "role" in user_data:
            user.role = user_data["role"]
        if "fullname" in user_data:
            user.fullname = user_data["fullname"]
        if "designation" in user_data:
            user.designation = user_data["designation"]
        if "approver" in user_data:
            user.approver = user_data["approver"]
        db.session.commit()
        return user


@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        """Refresh JWT Token."""
        current_user = get_jwt_identity()
        access_token_expires = timedelta(minutes=30)
        new_token = create_access_token(identity=current_user, fresh=False, expires_delta=access_token_expires)
        # Make it clear that when to add the refresh token to the blocklist will depend on the app design
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"access_token": new_token}, 200


@blp.route("/user")
class UserList(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema(many=True))
    def get(self):
        """Get a list of all users."""
        users = UserModel.query.all()
        return users

