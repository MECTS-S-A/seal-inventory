from ldap3 import Server, Connection
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