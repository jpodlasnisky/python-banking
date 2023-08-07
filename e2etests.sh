#!/bin/bash

echo New Account Alice:

curl -s -H "Content-Type: application/json" -X POST -d '{"full_name": "alice", "email_address":"alice@example.com","password":"alice"}' http://localhost:5000/api/v1/signup

echo New Account Bob:

curl -s -H "Content-Type: application/json" -X POST -d '{"full_name": "bob", "email_address":"bob@example.com","password":"bob"}' http://localhost:5000/api/v1/signup

echo Login Alice:

ALICETOKEN=$(curl -s -H "Content-Type: application/json" -X POST -d '{"email_address":"alice@example.com","password":"alice"}' http://localhost:5000/api/v1/auth | jq -r ".access_token")
echo $ALICETOKEN
echo Login Bob:

BOBTOKEN=$(curl -s -H "Content-Type: application/json" -X POST -d '{"email_address":"bob@example.com","password":"bob"}' http://localhost:5000/api/v1/auth | jq -r ".access_token")
echo $BOBTOKEN
echo Get Account Alice:

ALICE=$(curl -s -H "Content-Type: application/json" -X GET http://localhost:5000/api/v1/account -H "Authorization: Bearer $ALICETOKEN" | jq -r ".identity")
echo $ALICE 
ALICEBALANCE=$(curl -s -H "Content-Type: application/json" -X GET http://localhost:5000/api/v1/account -H "Authorization: Bearer $ALICETOKEN" | jq -r ".balance")
echo $ALICEBALANCE

echo Get Account Bob:

BOB=$(curl -s -H "Content-Type: application/json" -X GET http://localhost:5000/api/v1/account -H "Authorization: Bearer $BOBTOKEN" | jq -r ".identity")
echo $BOB 

echo Deposit 100 dollars Alice:

ALICEDEPOSIT=$(curl -s -H "Content-Type: application/json" -X POST http://localhost:5000/api/v1/deposit -H "Authorization: Bearer $ALICETOKEN" -d '{"amount": 10000}' | jq -r ".amount")

if [ "$ALICEDEPOSIT" = "10000" ]
then
echo Success
else
echo $ALICEDEPOSIT
echo Deposit Failed
exit 1
fi

echo Get Account Alice:

curl -s -H "Content-Type: application/json" -X GET http://localhost:5000/api/v1/account -H "Authorization: Bearer $ALICETOKEN"

echo Transfer 10 dollars to Bob:

TRANSFER='{"amount": 1000, "to_account_id": "'$BOB'"}'
echo $TRANSFER
curl -s -H "Content-Type: application/json" -X POST http://localhost:5000/api/v1/transfer -H "Authorization: Bearer $ALICETOKEN" -d "$TRANSFER"

echo Get Account Alice:

curl -s -H "Content-Type: application/json" -X GET http://localhost:5000/api/v1/account -H "Authorization: Bearer $ALICETOKEN"

echo Get Account Bob:

curl -s -H "Content-Type: application/json" -X GET http://localhost:5000/api/v1/account -H "Authorization: Bearer $BOBTOKEN"

echo Withdraw 10 dollars on Alice account:

ALICEWITHDRAW=$(curl -s -H "Content-Type: application/json" -X POST http://localhost:5000/api/v1/withdraw -H "Authorization: Bearer $ALICETOKEN" -d '{"amount": 10}' | jq -r ".message")

if [ "$ALICEWITHDRAW" = "success" ]
then
echo Success withdraw
else
echo $ALICEWITHDRAW
echo Deposit Failed
exit 1
fi

echo Withdraw 1000 dollars on Alice account:

TRANSFER=$(curl -s -H "Content-Type: application/json" -X POST http://localhost:5000/api/v1/withdraw -H "Authorization: Bearer $ALICETOKEN" -d '{"amount": 1000}' | jq -r ".message")

if [ "$TRANSFER" = "success" ]
then
echo Success withdraw
else
echo $TRANSFER
exit 1
fi


echo Transfer 10 dollars to unknown: 

TRANSFER='{"amount": 1000, "to_account_id": "00000000-0000-0000-0000-000000000000"}'
#RESULT=$(curl -s -H "Content-Type: application/json" -X POST http://localhost:5000/api/v1/transfer -H "Authorization: Bearer $ALICETOKEN" -d "$TRANSFER" | jq -r ".error")
STATUS_CODE=$(curl -o /dev/null -s -w "%{http_code}\n" -H "Content-Type: application/json" -X POST http://localhost:5000/api/v1/transfer -H "Authorization: Bearer $ALICETOKEN" -d "$TRANSFER" )
if [ "$STATUS_CODE" -eq 400 ]
then
echo Successfully blocked an invalid transfer
else
echo Failed, should have blocked an invalid transfer
echo $RESULT
exit 1
fi
