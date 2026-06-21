from datetime import datetime, timezone


def naive_utcnow() -> datetime:
    """UTC atual sem timezone (substitui datetime.utcnow(), deprecada no 3.12).

    Mantém datetimes "naive" para permanecer consistente com os valores
    persistidos no SQLite e evitar comparações entre naive e aware.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
