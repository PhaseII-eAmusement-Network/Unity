from sqlalchemy import URL, make_url
from getpass import getpass


def prompt(msg, optional=False):
    value = input(f"{msg}{' (optional)' if optional else ''}: ").strip()
    return value or None


def main():
    driver = prompt("Database driver (e.g. postgresql+psycopg2)")
    username = prompt("Username", optional=True)
    password = getpass("Password (hidden, optional): ") or None
    host = prompt("Host", optional=True)
    port_input = prompt("Port", optional=True)
    database = prompt("Database name", optional=True)

    # Safely parse port
    port = int(port_input) if port_input and port_input.isdigit() else None

    url = URL.create(
        drivername=driver,
        username=username,
        password=password,
        host=host,
        port=port,
        database=database,
    )

    rendered = url.render_as_string(hide_password=False)

    # Verify round-trip integrity
    assert make_url(rendered) == url

    print("\nSQLAlchemy connection string:")
    print(f"  {rendered!r}")

    # Escape for ConfigParser (e.g. alembic.ini)
    escaped = rendered.replace("%", "%%")

    # Verify escaped version still works with interpolation
    assert make_url(escaped % {}) == url

    print("\nConfigParser-safe (e.g. alembic.ini):")
    print(f"  sqlalchemy.url = {escaped}")


if __name__ == "__main__":
    main()