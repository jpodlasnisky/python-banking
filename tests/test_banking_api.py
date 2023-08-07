# coding=utf-8
"""Test banking API."""
import json
from banking.api import app

API_V1_PREFIX = "/api/v1"
CONTENT_TYPE = "application/json"

def test_open_account() -> None:
    client = app.test_client()

    # Open account for alice.
    data_new_account = {
        "full_name": "Alice",
        "email_address": "alice@example.com",
        "password": "alice",
    }
    response_alice = client.post(
        API_V1_PREFIX+"/signup",
        data=json.dumps(data_new_account),
        content_type=CONTENT_TYPE,
    )
    assert response_alice.status_code == 201
    assert response_alice.json["message"] == "created"
    assert response_alice.json["account_id"] is not None

    # open account for bob
    data_new_account = {
        "full_name": "Bob",
        "email_address": "bob1@example.com",
        "password": "bob",
    }
    response_bob = client.post(
        API_V1_PREFIX+"/signup",
        data=json.dumps(data_new_account),
        content_type=CONTENT_TYPE,
    )
    assert response_bob.status_code == 201
    assert response_bob.json["message"] == "created"
    assert response_bob.json["account_id"] is not None

    # Login alice.
    login_data = {
        "email_address": "alice@example.com",
        "password": "alice",
    }
    response_alice = client.post(
        API_V1_PREFIX+"/auth",
        data=json.dumps(login_data),
        content_type=CONTENT_TYPE,
    )

    assert response_alice.status_code == 200
    assert response_alice.json["message"] == "success"
    assert response_alice.json["access_token"] is not None

    # login bob
    login_data = {
        "email_address": "bob1@example.com",
        "password": "bob",
    }
    response_bob = client.post(
        API_V1_PREFIX+"/auth",
        data=json.dumps(login_data),
        content_type=CONTENT_TYPE,
    )

    assert response_bob.status_code == 200
    assert response_bob.json["message"] == "success"
    assert response_bob.json["access_token"] is not None

    # get token
    token = response_alice.json["access_token"]
    token_bob = response_bob.json["access_token"]

    # get account bob
    response_bob = client.get(
        API_V1_PREFIX+"/account",
        headers={"Authorization": f"Bearer {token_bob}"},
    )
    identity_bob = response_bob.json["identity"]

    assert response_bob.status_code == 200

    # deposit alice.
    data_deposit = {
        "amount": 100,
    }
    response_alice = client.post(
        API_V1_PREFIX+"/deposit",
        data=json.dumps(data_deposit),
        content_type=CONTENT_TYPE,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response_alice.status_code == 200
    assert response_alice.json["amount"] == "100"

    # Fail to deposit
    data_deposit = {
        "amount": 0,
    }
    response_alice = client.post(
        API_V1_PREFIX+"/deposit",
        data=json.dumps(data_deposit),
        content_type=CONTENT_TYPE,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response_alice.status_code == 400

    # Test withdraw
    data_withdraw = {
        "amount": 50,
    }
    response_alice = client.post(
        API_V1_PREFIX+"/withdraw",
        data=json.dumps(data_withdraw),
        content_type=CONTENT_TYPE,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response_alice.status_code == 200
    assert response_alice.json["message"] == "success"

    # Test transfer
    data_transfer = {
        "amount": 50,
        "to_account_id": identity_bob,
    }
    response_alice = client.post(
        API_V1_PREFIX+"/transfer",
        data=json.dumps(data_transfer),
        content_type=CONTENT_TYPE,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response_alice.status_code == 200
    assert response_alice.json["message"] == "success"


    # close alice account
    response_alice = client.post(
        API_V1_PREFIX+"/close_account",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response_alice.status_code == 200

    # get alice balance
    response_alice = client.get(
        API_V1_PREFIX+"/account/balance",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response_alice.status_code == 200
    assert response_alice.json["balance"] == str(0)

    # get alice overdraft limit
    response_alice = client.get(
        API_V1_PREFIX+"/account/overdraft_limit",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response_alice.status_code == 200
    assert response_alice.json["overdraft_limit"] == str(0)

    # set bob overdraft limit
    data_overdraft_limit = {
        "overdraft_limit": 100,
    }
    response_bob = client.post(
        API_V1_PREFIX+"/account/overdraft_limit",
        data=json.dumps(data_overdraft_limit),
        content_type=CONTENT_TYPE,
        headers={"Authorization": f"Bearer {token_bob}"},
    )
    assert response_bob.status_code == 200
    assert response_bob.json["message"] == "success"

    # change bob password
    data_change_password = {
        "old_password": "bob",
        "new_password": "bob2",
    }
    response_bob = client.post(
        API_V1_PREFIX+"/account/change_password",
        data=json.dumps(data_change_password),
        content_type=CONTENT_TYPE,
        headers={"Authorization": f"Bearer {token_bob}"},
    )
    assert response_bob.status_code == 200
    assert response_bob.json["message"] == "success"

    # fail set alice overdraft limit
    data_overdraft_limit = {
        "overdraft_limit": 100,
    }
    response_alice = client.post(
        API_V1_PREFIX+"/account/overdraft_limit",
        data=json.dumps(data_overdraft_limit),
        content_type=CONTENT_TYPE,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response_alice.status_code == 400

    # fail bob withdraw
    data_withdraw = {
        "amount": 10000,
    }
    response_bob = client.post(
        API_V1_PREFIX+"/withdraw",
        data=json.dumps(data_withdraw),
        content_type=CONTENT_TYPE,
        headers={"Authorization": f"Bearer {token_bob}"},
    )
    assert response_bob.status_code == 400

    # Fail to transfer from bob to an account the does not exist
    data_transfer = {
        "amount": 50,
        "to_account_id": "00000000-0000-0000-0000-000000000000",
    }
    response_bob = client.post(
        API_V1_PREFIX+"/transfer",
        data=json.dumps(data_transfer),
        content_type=CONTENT_TYPE,
        headers={"Authorization": f"Bearer {token_bob}"},
    )
    assert response_bob.status_code == 400



    # fail alice authentication wrong password

    login_data = {
        "email_address": "alice@example.com",
        "password": "alice2",
    }
    response_alice = client.post(
        API_V1_PREFIX+"/auth",
        data=json.dumps(login_data),
        content_type=CONTENT_TYPE,
    )

    assert response_alice.status_code == 401
