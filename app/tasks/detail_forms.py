from urllib.parse import urlsplit

from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, ValidationError

from app.tasks.forms import clean_text


class FrenchForm(FlaskForm):
    class Meta:
        locales = ("fr_FR", "fr")


class SubtaskForm(FrenchForm):
    title = StringField(
        "Nouvelle sous-tâche",
        filters=[clean_text],
        validators=[DataRequired("Écris la sous-tâche."), Length(max=120, message="120 caractères maximum.")],
    )


class CommentForm(FrenchForm):
    body = TextAreaField(
        "Commentaire",
        filters=[clean_text],
        validators=[DataRequired("Le commentaire est vide."), Length(max=1000, message="1000 caractères maximum.")],
    )


class LinkForm(FrenchForm):
    url = StringField(
        "Adresse du lien",
        filters=[clean_text],
        validators=[DataRequired("Indique l'adresse du lien."), Length(max=500, message="500 caractères maximum.")],
    )
    label = StringField(
        "Titre du lien",
        filters=[clean_text],
        validators=[Optional(), Length(max=80, message="80 caractères maximum.")],
    )

    def validate_url(self, field):
        parts = urlsplit(field.data or "")
        if parts.scheme not in ("http", "https") or not parts.hostname:
            raise ValidationError("Le lien doit commencer par https:// ou http://.")
        if parts.username or parts.password or any(character.isspace() for character in field.data):
            raise ValidationError("Ce lien n'est pas valide.")


class AttachmentForm(FrenchForm):
    file = FileField("Fichier")
