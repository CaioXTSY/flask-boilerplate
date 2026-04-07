from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import BooleanField, EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError


class LoginForm(FlaskForm):
    email = EmailField(
        "E-mail",
        validators=[DataRequired(message="E-mail é obrigatório."), Email(message="E-mail inválido.")],
    )
    password = PasswordField(
        "Senha",
        validators=[DataRequired(message="Senha é obrigatória.")],
    )
    remember_me = BooleanField("Lembrar de mim")
    submit = SubmitField("Entrar")


class RegisterForm(FlaskForm):
    username = StringField(
        "Nome de usuário",
        validators=[
            DataRequired(message="Nome de usuário é obrigatório."),
            Length(min=3, max=64, message="O nome de usuário deve ter entre 3 e 64 caracteres."),
            Regexp(
                r"^[A-Za-z0-9]+$",
                message="O nome de usuário deve conter apenas letras e números.",
            ),
        ],
    )
    email = EmailField(
        "E-mail",
        validators=[
            DataRequired(message="E-mail é obrigatório."),
            Email(message="E-mail inválido."),
        ],
    )
    password = PasswordField(
        "Senha",
        validators=[
            DataRequired(message="Senha é obrigatória."),
            Length(min=8, message="A senha deve ter no mínimo 8 caracteres."),
        ],
    )
    password2 = PasswordField(
        "Confirmar senha",
        validators=[
            DataRequired(message="Confirmação de senha é obrigatória."),
            EqualTo("password", message="As senhas não coincidem."),
        ],
    )
    submit = SubmitField("Criar conta")

    def validate_username(self, field: StringField) -> None:
        from app.models.user import User

        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Este nome de usuário já está em uso.")

    def validate_email(self, field: EmailField) -> None:
        from app.models.user import User

        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Este e-mail já está cadastrado.")
