"""
MicroBank Integration Test Script
----------------------------------
Runs a full end‑to‑end flow: register, login, create accounts, deposit,
transfer, transaction history, interest calculation, and admin checks.

Usage:
    set AUTH_URL=http://localhost:8001
    set ACCOUNT_URL=http://localhost:8002
    set TRANSACTION_URL=http://localhost:8003
    set ADMIN_URL=http://localhost:8004
    set ADMIN_EMAIL=admin@example.com      # optional, if you want to test admin endpoints
    set ADMIN_PASSWORD=Admin123
    python tests/integration_test.py
"""

import os
import sys
import uuid
import time
import httpx

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
BASE = {
    "auth": os.getenv("AUTH_URL", "http://localhost:8001"),
    "account": os.getenv("ACCOUNT_URL", "http://localhost:8002"),
    "transaction": os.getenv("TRANSACTION_URL", "http://localhost:8003"),
    "admin": os.getenv("ADMIN_URL", "http://localhost:8004"),
}

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@123")


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")


def run_tests():
    with httpx.Client() as client:

        # 1. Register a new customer
        log("Registering customer1 ...")
        customer1 = {
            "full_name": "Alice",
            "email": f"alice_{uuid.uuid4().hex[:6]}@test.com",
            "password": "Alice123",
        }
        r = client.post(f"{BASE['auth']}/register", json=customer1)
        assert r.status_code == 201, f"Register failed: {r.text}"
        user1_id = r.json()["user_id"]
        log(f"Customer1 registered: {user1_id}")

        # 2. Login as customer1
        log("Logging in customer1 ...")
        r = client.post(
            f"{BASE['auth']}/login",
            data={"username": customer1["email"], "password": customer1["password"]},
        )
        assert r.status_code == 200, f"Login failed: {r.text}"
        token1 = r.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        # 3. Create account for customer1
        log("Creating account for customer1 ...")
        r = client.post(f"{BASE['account']}/", headers=headers1)
        assert r.status_code == 201, f"Create account failed: {r.text}"
        acc1 = r.json()
        log(f"Account: {acc1['account_number']}, balance: {acc1['balance']}")

        # 4. Deposit money
        log("Depositing 10,000 ...")
        r = client.post(
            f"{BASE['transaction']}/deposit",
            json={"amount": 10000},
            headers=headers1,
        )
        assert r.status_code == 200, f"Deposit failed: {r.text}"
        log(f"Balance after deposit: {r.json()['updated_balance']}")

        # 5. Register a second customer
        log("Registering customer2 ...")
        customer2 = {
            "full_name": "Bob",
            "email": f"bob_{uuid.uuid4().hex[:6]}@test.com",
            "password": "Bob123",
        }
        r = client.post(f"{BASE['auth']}/register", json=customer2)
        assert r.status_code == 201, f"Register customer2 failed: {r.text}"
        r = client.post(
            f"{BASE['auth']}/login",
            data={"username": customer2["email"], "password": customer2["password"]},
        )
        token2 = r.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        r = client.post(f"{BASE['account']}/", headers=headers2)
        assert r.status_code == 201, f"Create account for customer2 failed: {r.text}"
        acc2 = r.json()
        log(f"Customer2 account: {acc2['account_number']}")

        # 6. Transfer money
        log("Transferring 500 from customer1 to customer2 ...")
        r = client.post(
            f"{BASE['transaction']}/transfer",
            json={
                "receiver_account_number": acc2["account_number"],
                "amount": 500,
            },
            headers=headers1,
        )
        assert r.status_code == 200, f"Transfer failed: {r.text}"
        transfer_data = r.json()
        log(f"Transfer ID: {transfer_data['transaction_id']}")
        log(f"Sender balance: {transfer_data['sender_balance']}")

        # Verify receiver balance
        r = client.get(f"{BASE['account']}/balance", headers=headers2)
        assert float(r.json()["balance"]) == 500.0, "Receiver balance mismatch"
        log("Receiver balance is correct.")

        # 7. Transaction history
        log("Checking transaction history ...")
        r = client.get(f"{BASE['transaction']}/history", headers=headers1)
        assert r.status_code == 200
        history = r.json()
        assert len(history) >= 2, "History should have at least deposit and transfer"
        log(f"History contains {len(history)} transactions.")

        # 8. Transaction detail
        txn_id = transfer_data["transaction_id"]
        r = client.get(f"{BASE['transaction']}/{txn_id}", headers=headers1)
        assert r.status_code == 200
        detail = r.json()
        assert detail["transaction_type"] == "TRANSFER"
        log("Transaction detail verified.")

        # 9. Admin tests (if admin credentials are provided)
        if ADMIN_EMAIL and ADMIN_PASSWORD:
            log("Testing admin endpoints ...")
            # Attempt login as admin (may fail if not promoted – we’ll handle gracefully)
            r = client.post(
                f"{BASE['auth']}/login",
                data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            )
            if r.status_code != 200:
                log(f"Admin login failed – make sure {ADMIN_EMAIL} is an ADMIN user.")
                log("Skipping admin tests.")
            else:
                admin_token = r.json()["access_token"]
                admin_headers = {"Authorization": f"Bearer {admin_token}"}

                # List users
                r = client.get(f"{BASE['admin']}/users", headers=admin_headers)
                assert r.status_code == 200
                users = r.json()
                log(f"Total users: {len(users)}")

                # List accounts
                r = client.get(f"{BASE['admin']}/accounts", headers=admin_headers)
                assert r.status_code == 200
                log(f"Total accounts: {len(r.json())}")

                # Trigger interest calculation
                log("Triggering interest calculation ...")
                r = client.post(f"{BASE['admin']}/interest/apply", headers=admin_headers)
                assert r.status_code == 200, f"Interest trigger failed: {r.text}"
                log("Interest task started. Waiting 3 seconds for Celery...")
                time.sleep(3)

                # Check that balance increased
                r = client.get(f"{BASE['account']}/balance", headers=headers1)
                new_balance = float(r.json()["balance"])
                log(f"Customer1 balance after interest: {new_balance}")
                assert new_balance > 9500, "Interest should have increased balance"
                log("Interest applied successfully!")

        log("All integration tests passed! 🎉")


if __name__ == "__main__":
    try:
        run_tests()
    except AssertionError as e:
        log(f"TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        log(f"UNEXPECTED ERROR: {e}")
        sys.exit(1)