"""
Database objects.

Flask database models initialization.
"""

from datetime import datetime

from app import db
from sqlalchemy_mptt.mixins import BaseNestedSets

# Assignment tables

user_module = db.Table(
    'assignment_users_modules',
    db.Column(
        'user_id',
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True
    ),
    db.Column(
        'module_id',
        db.Integer,
        db.ForeignKey('modules.id'),
        primary_key=True
    )
)

user_structure = db.Table(
    'assignment_users_structures',
    db.Column(
        'user_id',
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True
    ),
    db.Column(
        'structure_id',
        db.Integer,
        db.ForeignKey(
            'organizational_structure.id'
        ),
        primary_key=True
    )
)

# ------------------------------------------------------------------------------


class OrganizationalStructure(db.Model, BaseNestedSets):
    """Organizational structure model."""

    # __table_args__ = {'schema': 'innerInformationSystem_System'}

    id = db.Column(
        db.Integer,
        primary_key=True,
        comment="Уникальный идентификатор"
    )
    name = db.Column(db.String(100), comment="Имя элемента")
    type = db.Column(db.SmallInteger, comment="Тип элемента")
    deletable = db.Column(db.SmallInteger, comment="Удаляемый?", default=1)
    movable = db.Column(db.SmallInteger, comment="Двигаемый?", default=1)
    updatable = db.Column(db.SmallInteger, comment="Обновляемый?", default=1)
    insertable = db.Column(db.SmallInteger, comment="Потомки?", default=1)

    def __repr__(self):
        """Class representation string."""
        return 'Structure element «%r» of type «%r»' % (self.name, self.type)


class Users(db.Model):
    """System user model."""

    __tablename__ = 'users'
    # __table_args__ = {'schema': 'innerInformationSystem_System'}
    id = db.Column(
        db.Integer,
        primary_key=True,
        comment="Уникальный идентификатор"
    )
    login = db.Column(db.String(20), unique=True, comment="Уникальный логин")
    photo = db.Column(db.String(50), comment="Имя файла фотокарточки")
    name = db.Column(db.String(20), comment="Имя")
    surname = db.Column(db.String(20), comment="Фамилия")
    patronymic = db.Column(db.String(20), comment="Отчество")
    phone = db.Column(db.String(13), unique=True, comment="Телефон")
    about_me = db.Column(db.Text(), comment="О себе (например, должность)")

    birth_date = db.Column(db.Date, comment="Дата рождения")
    employment_date = db.Column(db.Date, comment="Дата трудоустройства")

    status = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        comment="Статус записи пользователя"
    )

    modules = db.relationship(
        'Modules',
        secondary=user_module,
        lazy='subquery',
        backref=db.backref('users', lazy=True)
    )

    structures = db.relationship(
        'OrganizationalStructure',
        secondary=user_structure,
        lazy='subquery',
        backref=db.backref('users', lazy=True)
    )

    emails = db.relationship('Emails', backref='users', lazy='dynamic')
    passwords = db.relationship('Passwords', backref='users', lazy='dynamic')

    # def __init__(self, login, password,
    #              name, surname, patronymic,
    #              email, phone, birth_date, about_me=None,
    #              last_login=None, status=None, socials=None, photo=None):
    # """Конструктор класса."""
    # self.login = login
    # self.password = {
    #     "value": bcrypt.generate_password_hash(password).decode('utf-8'),
    #     "blocked": False,
    #     "first_auth": True,
    #     "activeUntil": (datetime.now() + relativedelta(
    #                             months=1)).isoformat(),
    #     "failed_times": 0
    # }
    # self.socials = {"ok": "",
    #                 "vk": "",
    #                 "google": "",
    #                 "yandex": ""} if socials is None else socials
    # self.photo = None if photo is None else photo
    # self.name = name
    # self.surname = surname
    # self.patronymic = patronymic
    # self.email = cms_user_emails(email)
    # self.phone = phone
    # self.birth_date = birth_date
    # self.last_login = None if last_login is None else last_login
    # self.status = 1 if status is None else status
    # self.about_me = '' if about_me is None else about_me

    def __repr__(self):
        """Class representation string."""
        return 'User with login: %r ' % (self.login)


class ModulesTypes(db.Model):
    """
    Modules types model.

    Static DB table. Just GET and PUT methods.
    """

    __tablename__ = 'modules_types'
    # __table_args__ = {'schema': 'innerInformationSystem_System'}
    id = db.Column(
        db.Integer,
        primary_key=True,
        comment="Уникальный идентификатор"
    )
    name = db.Column(db.String(50), comment="Имя типа модуля")
    code = db.Column(db.String(36), comment="Уникальный код")

    modules = db.relationship(
        'Modules',
        backref='type',
        lazy='dynamic',
        uselist=True
    )

    def __repr__(self):
        """Class representation string."""
        return 'Module type «%r»' % (self.name)


class Modules(db.Model):
    """
    Modules model.

    Static DB table. Just GET and PUT methods.
    """

    __tablename__ = 'modules'
    # __table_args__ = {'schema': 'innerInformationSystem_System'}
    id = db.Column(
        db.Integer,
        primary_key=True,
        comment="Уникальный идентификатор"
    )
    name = db.Column(db.String(50), comment="Имя модуля")
    description = db.Column(db.String(256), comment="Короткое описание модуля")
    version = db.Column(db.String(8), comment="Версия модуля")
    code = db.Column(db.String(36), comment="Уникальный код")

    module_type_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "modules_types.id"
        ),
        nullable=False,
        comment="Тип модуля"
    )

    def __repr__(self):
        """Class representation string."""
        return 'Module «%r»' % (self.name)


class Emails(db.Model):
    """Emails for users model."""

    __tablename__ = 'emails'
    # __table_args__ = {'schema': 'innerInformationSystem_System'}
    id = db.Column(
        db.Integer,
        primary_key=True,
        comment="Уникальный идентификатор"
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id"
        ),
        comment="Пользователь"
    )
    value = db.Column(db.String(100), comment="Адрес почты")
    type = db.Column(db.String(20), comment="Тип почты", nullable=True)
    main = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        comment="Основная"
    )
    verify = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        comment="Подтверждение"
    )
    active_until = db.Column(
        db.DateTime,
        default=None,
        nullable=True,
        comment="Активна до"
    )

    def __repr__(self):
        """Class representation string."""
        return 'Email «%r»' % (self.value)


class Passwords(db.Model):
    """Passwords for users model."""

    __tablename__ = 'passwords'
    # __table_args__ = {'schema': 'innerInformationSystem_System'}
    id = db.Column(
        db.Integer,
        primary_key=True,
        comment="Уникальный идентификатор"
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id"
        ),
        comment="Пользователь"
    )
    value = db.Column(db.String(100), comment="Захешированный пароль")
    blocked = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        comment="Статус блокировки пароля"
    )
    nubmer_of_uses = db.Column(
        db.Integer,
        default=0,
        nullable=False,
        comment="Количество использований"
    )
    created_at = db.Column(
        db.DateTime,
        default=datetime.now(),
        nullable=True,
        comment="Создан"
    )
    active_until = db.Column(
        db.DateTime,
        default=None,
        nullable=True,
        comment="Активна до"
    )

    def __repr__(self):
        """Class representation string."""
        return 'Password %i «%r» for user «%r»' % (
            self.id,
            self.value,
            self.user_id
        )
