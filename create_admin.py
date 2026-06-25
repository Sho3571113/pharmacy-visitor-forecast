from register_user import register_user

success, message = register_user(
    username="admin",
    display_name="管理者",
    password="admin123",
    role="admin"
)

print(message)