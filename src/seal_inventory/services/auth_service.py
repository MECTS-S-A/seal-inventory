from ldap3 import Server, Connection
import os
from ldap3 import Server
from ldap3 import Connection
from ldap3 import SUBTREE
import os


class AuthService:

    def authenticate(self, username: str, password: str) -> bool:
        server = Server(os.getenv("LDAP_SERVER"))

        # normalize username
        clean_username = username.split("@")[0].split("\\")[-1]

        possible_users = [
            f"{clean_username}@Mects.local",
            f"MECTS\\{clean_username}",
        ]

        for user in possible_users:
            try:
                Connection(server, user=user, password=password, auto_bind=True)
                print(f"LDAP SUCCESS: {user}")
                return True
            except Exception as e:
                print(f"LDAP FAIL: {user} -> {e}")
                continue

        return False





    def get_users(self):

        server = Server(
            os.getenv("LDAP_SERVER")
        )

        conn = Connection(
            server,
            user=os.getenv("LDAP_BIND_USER"),
            password=os.getenv("LDAP_BIND_PASSWORD"),
            auto_bind=True,
        )

        conn.search(
            search_base=os.getenv("LDAP_BASE_DN"),
            search_filter="(&(objectClass=user))",
            search_scope=SUBTREE,
            attributes=[
                "displayName",
                "sAMAccountName",
            ],
        )

        users = []

        for entry in conn.entries:

            users.append(
                {
                    "username": str(
                        entry.sAMAccountName
                    ),
                    "name": str(
                        entry.displayName
                    ),
                }
            )

        return users