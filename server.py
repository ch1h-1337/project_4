from flask import Flask, request, jsonify, render_template, redirect
from flasgger import Swagger
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2 import DatabaseError

# Загрузка переменных окружения
load_dotenv()

app = Flask(__name__)
swagger = Swagger(app)
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

# Подключение к базе данных
try:
    conn = psycopg2.connect(
        dbname="qw2",
        user="postgres",
        password="123",
        host="localhost",
        port="5432"
    )
    conn.autocommit = True
    cur = conn.cursor()
    print("Подключение к базе данных успешно!")
except DatabaseError as e:
    print(f"Ошибка подключения к базе данных: {e}")
    exit()


# ---------------- JWT АУТЕНТИФИКАЦИЯ ---------------- #

@app.route('/auth', methods=['GET'])
def auth_page():
    return render_template('login.html')


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username и password обязательны"}), 400

    # Проверяем, есть ли пользователь в базе данных
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    existing_user = cur.fetchone()

    if existing_user:
        return jsonify({"error": "Пользователь уже существует"}), 409

    # Хэшируем пароль
    password_hash = generate_password_hash(password)

    # Вставляем нового пользователя в базу данных
    cur.execute(
        "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
        (username, password_hash)
    )
    return jsonify({"message": "Регистрация успешна"}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Находим пользователя в базе данных
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()

    if not user or not check_password_hash(user[2], password):  # user[2] - это password_hash
        return jsonify({"error": "Неверные учетные данные"}), 401

    # Создаем JWT токен
    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200


@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token), 200


@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    user = get_jwt_identity()
    return jsonify({"message": f"Привет, {user}!"})


# ------------------ ПРОСТЫЕ СТРАНИЦЫ ------------------ #

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(host="localhost", port=5000, debug=True)