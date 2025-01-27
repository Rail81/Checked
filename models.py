from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db

class Организация(db.Model):
    __tablename__ = 'организации'
    id = db.Column(db.Integer, primary_key=True)
    название = db.Column(db.String(255), nullable=False)
    отделы = db.relationship('Отдел', backref='организация', lazy=True)

class Отдел(db.Model):
    __tablename__ = 'отделы'
    id = db.Column(db.Integer, primary_key=True)
    название = db.Column(db.String(255), nullable=False)
    организация_id = db.Column(db.Integer, db.ForeignKey('организации.id'), nullable=False)
    сотрудники = db.relationship('Сотрудник', backref='отдел', lazy=True)
    документы = db.relationship('Документ', backref='отдел', lazy=True)

class Сотрудник(UserMixin, db.Model):
    __tablename__ = 'сотрудники'
    id = db.Column(db.Integer, primary_key=True)
    отдел_id = db.Column(db.Integer, db.ForeignKey('отделы.id'), nullable=False)
    telegram_id = db.Column(db.BigInteger, unique=True)
    фамилия = db.Column(db.String(100), nullable=False)
    имя = db.Column(db.String(100), nullable=False)
    отчество = db.Column(db.String(100))
    табельный_номер = db.Column(db.String(20), unique=True, nullable=False)
    должность = db.Column(db.String(255))
    рабочий_телефон = db.Column(db.String(20))
    email = db.Column(db.String(255), unique=True, nullable=False)
    пароль = db.Column(db.String(255), nullable=False)
    роль = db.Column(db.String(20), default='сотрудник')  # администратор, руководитель, сотрудник
    статус_регистрации = db.Column(db.Boolean, default=False)
    прочтения = db.relationship('ПрочтениеДокумента', backref='сотрудник', lazy=True)

    @property
    def полное_имя(self):
        if self.отчество:
            return f"{self.фамилия} {self.имя} {self.отчество}"
        return f"{self.фамилия} {self.имя}"

class Документ(db.Model):
    __tablename__ = 'документы'
    id = db.Column(db.Integer, primary_key=True)
    отдел_id = db.Column(db.Integer, db.ForeignKey('отделы.id'), nullable=False)
    название = db.Column(db.String(255), nullable=False)
    путь_к_файлу = db.Column(db.Text)
    срок_ознакомления = db.Column(db.Date)
    тип_документа = db.Column(db.String(50))
    дата_создания = db.Column(db.DateTime, default=datetime.utcnow)
    qr_код = db.Column(db.String(255))
    прочтения = db.relationship('ПрочтениеДокумента', backref='документ', lazy=True)

class ПрочтениеДокумента(db.Model):
    __tablename__ = 'прочтения_документов'
    id = db.Column(db.Integer, primary_key=True)
    сотрудник_id = db.Column(db.Integer, db.ForeignKey('сотрудники.id'), nullable=False)
    документ_id = db.Column(db.Integer, db.ForeignKey('документы.id'), nullable=False)
    дата_прочтения = db.Column(db.DateTime, default=datetime.utcnow)
    подтверждено = db.Column(db.Boolean, default=False)
