ADMINS = [
            ("Greg Farrell", "quozl@gruntomatic.com"),
            ]

CONTACT_EMAIL="quozl@gruntomatic.com"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2", # Add "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".
        "NAME": "gruntz_dev",                       # Or path to database file if using sqlite3.
        "USER": "gruntz",                             # Not used with sqlite3.
        "PASSWORD": "blah",                         # Not used with sqlite3.
        "HOST": "",                             # Set to empty string for localhost. Not used with sqlite3.
        "PORT": "",                             # Set to empty string for default. Not used with sqlite3.
    }
}

TIME_ZONE = "Europe/Dublin"

# Make this unique, and don't share it with anybody.
SECRET_KEY = "3*bh$*a(4ckv9i4%#z@gfdeebk6#yxz06(&^2v^^f7@7sia+-)"
