import sys
from pathlib import Path

import mysql.connector
import configparser

class DatabaseConnector:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connection = None
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """
        Loads configuration from the configuration file.
        :return:
        """
        try:
            path = DatabaseConnector.get_configuration_files_folder_path() / "config.ini"
            config = configparser.ConfigParser()
            with open(path, 'r') as f:
                config.read_file(f)

            section = config["mysql"]
            self._host = section["host"]
            self._database = section["database"]
            self._user = section["user"]
            self._password = section["password"]
        except FileNotFoundError:
            raise RuntimeError("Configuration file not found.")
        except KeyError as e:
            raise RuntimeError(f"Missing required config key: {e}.")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize configuration: {e}")

    def connect(self):
        """
        Connects to MySQL database.
        :return:
        """
        if self._connection is None or not self._connection.is_connected():
            self._connection = mysql.connector.connect(
                host=self._host,
                user=self._user,
                password=self._password,
                database=self._database,
                use_pure=True
            )
        return self._connection

    @staticmethod
    def get_configuration_files_folder_path():
        """
        Creates path to the configuration folder.
        :return:
        """
        if getattr(sys, 'frozen', False):
            base_path = Path(sys.executable).parent
        else:
            base_path = Path(__file__).resolve().parent.parent.parent

        config_dir = base_path / "configuration_files"

        if config_dir.exists():
            return config_dir

        alt_config_dir = base_path / "dist" / "configuration_files"
        if alt_config_dir.exists():
            return alt_config_dir

        raise RuntimeError(f"Configuration folder not found at: {config_dir}")
