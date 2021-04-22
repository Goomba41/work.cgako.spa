"""
Database objects.

Flask database models initialization.
"""

from app import db
from sqlalchemy_mptt.mixins import BaseNestedSets


class OrganizationalStructure(db.Model, BaseNestedSets):
    """Organizational structure model."""

    # __table_args__ = {'schema': 'innerInformationSystem_System'}
    # Приводит к багу
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
    __table_args__ = {'schema': 'innerInformationSystem_System'}
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
    phone = db.Column(db.String(14), unique=True, comment="Телефон")
    about_me = db.Column(db.Text(), comment="О себе (например, должность)")

    birth_date = db.Column(db.Date, comment="Дата рождения")
    employment_date = db.Column(db.Date, comment="Дата трудоустройства")

    status = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        comment="Статус записи пользователя"
    )

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
    __table_args__ = {'schema': 'innerInformationSystem_System'}
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


class Roles(db.Model):
    """System roles model."""

    __table_args__ = {'schema': 'innerInformationSystem_System'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    # users = db.relationship('Users', backref='roles', lazy='dynamic')
# permission = db.relationship('Permission', backref='role', lazy='dynamic')

    def __repr__(self):
        """Class representation string."""
        return 'Role «%r»' % (self.name)
