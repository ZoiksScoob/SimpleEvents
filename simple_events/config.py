import os

# Place the db within the simple_events directory
sqlite_local_base = 'sqlite:///'
database_name = 'simple_events.db'
basedir = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(basedir, database_name)


class BaseConfig:
    """Base configuration."""
    SECRET_KEY = os.environ['SECRET_KEY']
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RESTPLUS_VALIDATE = True
    AUTH_TOKEN_EXPIRY_SECONDS = int(os.environ.get('AUTH_TOKEN_EXPIRY_SECONDS', 60 * 60))


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = sqlite_local_base + database_path


class TestingConfig(BaseConfig):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    # In memory database
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    AUTH_TOKEN_EXPIRY_SECONDS = 5


class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = sqlite_local_base + database_path


configs = dict(
    DevelopmentConfig=DevelopmentConfig,
    TestingConfig=TestingConfig,
    ProductionConfig=ProductionConfig
)
