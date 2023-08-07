# coding=utf-8
# flake8: noqa E402

import logging
from typing import Dict, Tuple
from uuid import UUID
from eventsourcing.application import AggregateNotFound
from flask import Flask, Response, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity  # type: ignore
from flask_restful import Resource, Api  # type: ignore


from banking.applicationmodel import Bank
from banking.utils.http_errors import handler

from banking.domainmodel import Account, AccountClosedError, BadCredentials

logging.basicConfig(level=logging.INFO)


app = Flask(__name__)
app.config["SECRET_KEY"] = "super-secret"
app.config["JWT_EXPIRATION_DELTA"] = 3600
app.config["JWT_DEFAULT_REALM"] = "Login Required"
jwt = JWTManager(app)

api = Api(app, prefix="/api/v1")

_bank = Bank()


def bank() -> Bank:
    return _bank


class User:
    def __init__(self, id: str):
        self.id = id


def user() -> User:
    account = bank().get_account(UUID(get_jwt_identity()))
    return User(id=str(account.id))


class AccountResource(Resource):
    @jwt_required()
    @handler
    def get(self) -> Tuple[Dict[str, str], int]:
        account = bank().get_account(UUID(user().id))
        return {
            "balance": str(account.balance),
            "identity": user().id,
        }, 200


class DepositResource(Resource):
    @jwt_required()
    @handler
    def post(self) -> Tuple[Dict[str, str], int]:
        data = request.get_json()
        amount = data["amount"]
        account = bank().get_account(UUID(user().id))
        bank().deposit_funds(account.id, amount)
        return {
            "amount": str(amount),
        }, 200


class WithdrawResource(Resource):
    @jwt_required()
    @handler
    def post(self) -> Tuple[Dict[str, str], int]:
        data = request.get_json()
        amount = data["amount"]
        account = bank().get_account(UUID(user().id))
        bank().withdraw_funds(account.id, amount)
        return {
            "message": "success",
        }, 200


class TransferResource(Resource):
    @jwt_required()
    @handler
    def post(self) -> Tuple[Dict[str, str], int]:
        data = request.get_json()
        amount = data["amount"]
        to_account_id = UUID(data["to_account_id"])
        account = bank().get_account(UUID(user().id))
        try:
            bank().transfer_funds(account.id, to_account_id, amount)
            return {
                "message": "success",
            }, 200
        except:
            return {
                "error": "Transfer failed",
            }, 400

class CloseAccountResource(Resource):
    @jwt_required()
    @handler
    def post(self) -> Tuple[Dict[str, str], int]:
        account = bank().get_account(UUID(user().id))
        bank().close_account(account.id)
        return {
            "message": "success",
        }, 200


class AccountGetBalanceResource(Resource):
    @jwt_required()
    @handler
    def get(self) -> Tuple[Dict[str, str], int]:
        account = bank().get_account(UUID(user().id))
        return {
            "balance": str(account.balance),
        }, 200


class AccountGetOverdraftLimitResource(Resource):
    @jwt_required()
    @handler
    def get(self) -> Tuple[Dict[str, str], int]:
        account = bank().get_account(UUID(user().id))
        return {
            "overdraft_limit": str(account.overdraft_limit),
        }, 200


class AccountSetOverdraftLimitResource(Resource):
    @jwt_required()
    @handler
    def post(self) -> Tuple[Dict[str, str], int]:
        data = request.get_json()
        overdraft_limit = data["overdraft_limit"]
        account = bank().get_account(UUID(user().id))
        bank().set_overdraft_limit(account.id, overdraft_limit)
        return {
            "message": "success",
        }, 200


class AuthResource(Resource):
    @handler
    def post(self) -> Tuple[Dict[str, str], int]:
        data = request.get_json()
        email_address = data["email_address"]
        password = data["password"]
        account_id = bank().authenticate(email_address, password)
        return {
            "message": "success",
            "access_token": create_access_token(identity=str(account_id)),
        }, 200


class SignUpResource(Resource):
    @handler
    def post(self) -> Tuple[Dict[str, str], int]:
        data = request.get_json()
        full_name = data["full_name"]
        email_address = data["email_address"]
        password = data["password"]
        account_id = bank().open_account(full_name, email_address, password)
        return {
            "message": "created",
            "account_id": str(account_id),
        }, 201


class ChangePasswordResource(Resource):
    @jwt_required()
    @handler
    def post(self) -> Tuple[Dict[str, str], int]:
        data = request.get_json()
        old_password = data["old_password"]
        new_password = data["new_password"]
        account = bank().get_account(UUID(user().id))
        bank().change_password(account.id, old_password, new_password)
        return {
            "message": "success",
        }, 200


api.add_resource(AccountResource, "/account")
api.add_resource(DepositResource, "/deposit")
api.add_resource(WithdrawResource, "/withdraw")
api.add_resource(TransferResource, "/transfer")
api.add_resource(AuthResource, "/auth")
api.add_resource(SignUpResource, "/signup")
api.add_resource(CloseAccountResource, "/close_account")
api.add_resource(AccountGetBalanceResource, "/account/balance")
api.add_resource(AccountGetOverdraftLimitResource, "/account/overdraft_limit")
api.add_resource(AccountSetOverdraftLimitResource, "/account/overdraft_limit")
api.add_resource(ChangePasswordResource, "/account/change_password")
