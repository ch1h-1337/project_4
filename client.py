import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
)

API_BASE = "http://localhost:5000"

class AuthClient(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Клиент магазина игр")
        self.token = None

        # --- UI ---
        self.layout = QVBoxLayout()

        self.user_label = QLabel("Имя пользователя:")
        self.user_input = QLineEdit()
        self.pass_label = QLabel("Пароль:")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_btn = QPushButton("Войти")
        self.register_btn = QPushButton("Зарегистрироваться")
        self.protected_btn = QPushButton("Получить защищенные данные")
        self.protected_btn.setEnabled(False)

        self.login_btn.clicked.connect(self.login)
        self.register_btn.clicked.connect(self.register)
        self.protected_btn.clicked.connect(self.access_protected)

        self.layout.addWidget(self.user_label)
        self.layout.addWidget(self.user_input)
        self.layout.addWidget(self.pass_label)
        self.layout.addWidget(self.pass_input)
        self.layout.addWidget(self.login_btn)
        self.layout.addWidget(self.register_btn)
        self.layout.addWidget(self.protected_btn)

        self.setLayout(self.layout)

    def register(self):
        username = self.user_input.text()
        password = self.pass_input.text()

        if not username or not password:
            self.show_error("Введите имя пользователя и пароль.")
            return

        response = requests.post(f"{API_BASE}/api/register", json={
            "username": username,
            "password": password
        })

        if response.ok:
            self.show_message("Регистрация прошла успешно!")
        else:
            self.show_error(response.json().get("error", "Ошибка регистрации"))

    def login(self):
        username = self.user_input.text()
        password = self.pass_input.text()

        if not username or not password:
            self.show_error("Введите имя пользователя и пароль.")
            return

        response = requests.post(f"{API_BASE}/api/login", json={
            "username": username,
            "password": password
        })

        if response.ok:
            self.token = response.json()["access_token"]
            self.protected_btn.setEnabled(True)
            self.show_message("Вход выполнен!")
        else:
            self.show_error(response.json().get("error", "Ошибка входа"))

    def access_protected(self):
        if not self.token:
            self.show_error("Сначала выполните вход.")
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{API_BASE}/protected", headers=headers)

        if response.ok:
            message = response.json()["message"]
            self.show_message(f"Ответ от сервера: {message}")
        else:
            self.show_error("Ошибка доступа или токен устарел.")

    def show_message(self, msg):
        QMessageBox.information(self, "Успешно", msg)

    def show_error(self, msg):
        QMessageBox.critical(self, "Ошибка", msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = AuthClient()
    client.show()
    sys.exit(app.exec())
