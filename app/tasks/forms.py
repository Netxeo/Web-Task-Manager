import re
from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField, SelectField, StringField, TextAreaField
from wtforms.fields.choices import SelectChoice
from wtforms.validators import DataRequired, Length, Optional, ValidationError

from app.tasks.tags import parse_tags

CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
PRIORITY_CHOICES = [SelectChoice(0, "Aucune"), SelectChoice(1, "Basse"), SelectChoice(2, "Moyenne"), SelectChoice(3, "Haute")]
DUE_FORMAT = "%Y-%m-%dT%H:%M"


def clean_text(value):
    return CONTROL_CHARACTERS.sub("", value).strip() if isinstance(value, str) else value


class TaskForm(FlaskForm):
    class Meta:
        locales = ("fr_FR", "fr")

    title = StringField(
        "Titre",
        filters=[clean_text],
        validators=[DataRequired("Le titre est obligatoire."), Length(max=120, message="120 caractères maximum.")],
    )
    description = TextAreaField(
        "Description",
        filters=[clean_text],
        validators=[Optional(), Length(max=2000, message="2000 caractères maximum.")],
    )
    priority = SelectField("Priorité", choices=PRIORITY_CHOICES, coerce=int, default=0)
    due_at = DateTimeLocalField("Échéance", format=DUE_FORMAT, validators=[Optional()])
    tags = StringField(
        "Tags",
        filters=[clean_text],
        validators=[Optional(), Length(max=160, message="160 caractères maximum.")],
    )

    def validate_tags(self, field):
        try:
            parse_tags(field.data or "")
        except ValueError as error:
            raise ValidationError(str(error))

    def to_data(self):
        return {
            "title": self.title.data,
            "description": self.description.data or "",
            "priority": self.priority.data,
            "due_at": self.due_at.data.strftime(DUE_FORMAT) if self.due_at.data else None,
            "tags": parse_tags(self.tags.data or ""),
        }


def form_values(task):
    return {
        "title": task["title"],
        "description": task["description"],
        "priority": task["priority"],
        "due_at": datetime.strptime(task["due_at"], DUE_FORMAT) if task["due_at"] else None,
        "tags": ", ".join(task["tags"]),
    }
