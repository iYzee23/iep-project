from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class Role(database.Model):
    __tablename__ = "role"
    name = database.Column(database.String(8), primary_key=True)

    users = database.relationship("User", back_populates="role")


class User(database.Model):
    __tablename__ = "user"
    email = database.Column(database.String(256), primary_key=True)
    password = database.Column(database.String(256), nullable=False)
    forename = database.Column(database.String(256), nullable=False)
    surname = database.Column(database.String(256), nullable=False)
    role_name = database.Column(database.String(8), database.ForeignKey(Role.name), nullable=False)

    role = database.relationship("Role", back_populates="users")

    def __int__(self, email, password, forename, surname, role_name):
        self.email = email
        self.password = password
        self.forename = forename
        self.surname = surname
        self.role_name = role_name
