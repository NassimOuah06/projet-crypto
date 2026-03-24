class AppConfig:
    APP_NAME = "Hospital Management System"
    VERSION = "1.0.0"
    DEFAULT_THEME = "light"
    
    class Database:
        HOST = "localhost"
        PORT = 5432
        NAME = "hospital_db" 