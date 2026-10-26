from datetime import date, timedelta

DAY_NAMES = ("Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim")


def week_start(value=""):
    return date.fromisoformat(value) if value else date.today() - timedelta(days=date.today().weekday())


def week_days(monday):
    return [monday + timedelta(days=offset) for offset in range(7)]


def week_bounds(monday):
    return f"{monday:%Y-%m-%d}T00:00", f"{monday + timedelta(days=7):%Y-%m-%d}T00:00"


def shift_week(monday, weeks):
    return (monday + timedelta(weeks=weeks)).isoformat()
