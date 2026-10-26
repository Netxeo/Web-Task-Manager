import re
import unicodedata

TAG_PATTERN = re.compile(r"^[\w\- ]{1,24}$")
MAX_TAGS_PER_TASK = 5


def normalize_tag(name):
    cleaned = " ".join(unicodedata.normalize("NFKC", name).split()).lower()
    return cleaned if TAG_PATTERN.fullmatch(cleaned) else None


def parse_tags(text):
    names = []
    for raw in text.split(","):
        if not raw.strip():
            continue
        name = normalize_tag(raw)
        if name is None:
            raise ValueError(
                f"Tag invalide : « {raw.strip()[:24]} ». "
                "Lettres, chiffres, espaces, - et _ uniquement, 24 caractères maximum."
            )
        if name not in names:
            names.append(name)
    if len(names) > MAX_TAGS_PER_TASK:
        raise ValueError(f"{MAX_TAGS_PER_TASK} tags maximum par tâche.")
    return names


def set_task_tags(db, task_id, names):
    db.execute("DELETE FROM task_tags WHERE task_id = ?", (task_id,))
    for name in names:
        db.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (name,))
        db.execute(
            "INSERT INTO task_tags (task_id, tag_id) SELECT ?, id FROM tags WHERE name = ?",
            (task_id, name),
        )
    delete_orphan_tags(db)


def delete_orphan_tags(db):
    db.execute("DELETE FROM tags WHERE id NOT IN (SELECT tag_id FROM task_tags)")


def list_tags(db):
    return db.execute(
        "SELECT g.name, COUNT(*) AS total FROM tags g "
        "JOIN task_tags tt ON tt.tag_id = g.id GROUP BY g.id ORDER BY g.name"
    ).fetchall()
