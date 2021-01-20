"""
Database objects.

Flask database models initialization.
"""

from app import db


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
    password = db.Column(
        db.JSON(none_as_null=True),
        comment="Пароль и его параметры"
    )
    socials = db.Column(
        db.JSON(none_as_null=True),
        comment="Социальные сети"
    )
    photo = db.Column(db.String(50), comment="Имя файла фотокарточки")
    name = db.Column(db.String(20), comment="Имя")
    surname = db.Column(db.String(20), comment="Фамилия")
    patronymic = db.Column(db.String(20), comment="Отчество")
    email = db.Column(
        db.JSON(none_as_null=True),
        comment="Электронная почта и её параметры"
    )
    phone = db.Column(db.String(18), unique=True, comment="Телефон")
    about_me = db.Column(db.Text(), comment="О себе (например, должность)")

    birth_date = db.Column(db.Date, comment="Дата рождения")
    employment_date = db.Column(db.Date, comment="Дата трудоустройства")
    last_login = db.Column(
        db.JSON(none_as_null=True),
        comment="Данные последнего входа в систему"
    )

    status = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        comment="Статус записи пользователя"
    )

    department = db.Column(
        db.Integer,
        db.ForeignKey("innerInformationSystem_System.departments.id"),
        comment="Отдел"
    )
    department_position = db.Column(
        db.Integer,
        db.ForeignKey(
            "innerInformationSystem_System.departments_positions.id"
        ),
        comment="Должность"
    )
    role = db.Column(
        db.Integer,
        db.ForeignKey("innerInformationSystem_System.roles.id"),
        comment="Системная роль пользователя"
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


class Departments(db.Model):
    """Departments model."""

    __table_args__ = {'schema': 'innerInformationSystem_System'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    users = db.relationship('Users', backref='departments', lazy='dynamic')

    def __repr__(self):
        """Class representation string."""
        return 'Department «%r»' % (self.name)


class DepartmentsPositions(db.Model):
    """Departments positions model."""

    __table_args__ = {'schema': 'innerInformationSystem_System'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    users = db.relationship(
        'Users',
        backref='departments_positions',
        lazy='dynamic'
    )

    def __repr__(self):
        """Class representation string."""
        return 'Department position «%r»' % (self.name)


class Roles(db.Model):
    """System roles model."""

    __table_args__ = {'schema': 'innerInformationSystem_System'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    users = db.relationship('Users', backref='roles', lazy='dynamic')
# permission = db.relationship('Permission', backref='role', lazy='dynamic')

    def __repr__(self):
        """Class representation string."""
        return 'Role «%r»' % (self.name)
