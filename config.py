import os


class Config:
    # Basic Flask Config
    SECRET_KEY = '2963d38761f8725b847d5c6452ec8108'  # Replace with a secure key

    # MySQL Database Configurations
    MYSQL_DATABASE_USER = 'Mihir'  # Replace with your MySQL username
    MYSQL_DATABASE_PASSWORD = 'Mihir@20'  # Replace with your MySQL password
    MYSQL_DATABASE_DB = 'tryouts'  # Replace with your database name
    MYSQL_DATABASE_HOST = 'localhost'  # Replace if your database host is different
