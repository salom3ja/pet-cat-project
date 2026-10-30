import os
import time
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Настройки базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Настройки для загрузки картинок
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# Модель (таблица) для питомцев
class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    breed = db.Column(db.String(100), nullable=False) # Ошибка была тут, исправляем на db.String
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    likes = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Pet {self.name}>'

# Вспомогательная функция: проверяем, что файл - это картинка
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Создаем базу и добавляем первого питомца (если база пустая)
with app.app_context():
    db.create_all()
    if Pet.query.count() == 0:
        first_pet = Pet(
            name='Барсик',
            breed='Кот, дворовый аристократ',
            description='Любит спать на клавиатуре и воровать сосиски. Ищет друзей для совместного сна.',
            image_url='images.jpeg'
        )
        db.session.add(first_pet)
        db.session.commit()
        print('✅ Добавлен первый питомец: Барсик')

# Главная страница: показываем ленту
@app.route('/')
def index():
    # Забираем всех питомцев из базы, сортируя по новым (сначала последние добавленные)
    pets = Pet.query.order_by(Pet.id.desc()).all()
    return render_template('index.html', pets=pets)

# Новый маршрут: обработка формы добавления питомца
@app.route('/add', methods=['POST'])
def add_pet():
    # 1. Получаем данные из формы
    name = request.form.get('name')
    breed = request.form.get('breed')
    description = request.form.get('description')
    file = request.files.get('photo')

    # 2. Обрабатываем картинку
    image_url = 'images.jpeg' # Запасная картинка, если что-то пойдет не так
    if file and allowed_file(file.filename):
        # Делаем имя файла безопасным
        filename = secure_filename(file.filename)
        # Добавляем текущее время к имени, чтобы файлы с одинаковыми именами не перезаписывали друг друга
        unique_filename = f"{int(time.time())}_{filename}"
        # Сохраняем файл в папку static
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
        image_url = unique_filename

    # 3. Создаем новую запись в базе данных
    new_pet = Pet(
        name=name,
        breed=breed,
        description=description,
        image_url=image_url,
        likes=0
    )
    
    # 4. Сохраняем в базу
    db.session.add(new_pet)
    db.session.commit()

    # 5. Перенаправляем пользователя обратно на главную страницу
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
