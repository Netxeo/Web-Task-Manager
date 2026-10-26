from flask import render_template
from flask_wtf.csrf import CSRFError

ERROR_MESSAGES = {
    400: "La requête est invalide ou a expiré. Recharge la page et réessaie.",
    404: "Cette page ou cette tâche n'existe pas.",
    405: "Cette action n'est pas autorisée.",
    413: "Le contenu envoyé est trop volumineux.",
    429: "Trop de requêtes. Patiente quelques secondes.",
    500: "Une erreur inattendue est survenue.",
}


def render_error(code):
    return render_template("errors.html", code=code, message=ERROR_MESSAGES[code]), code


def init_app(app):
    for code in ERROR_MESSAGES:
        app.register_error_handler(code, lambda error, code=code: render_error(code))
    app.register_error_handler(CSRFError, lambda error: render_error(400))
