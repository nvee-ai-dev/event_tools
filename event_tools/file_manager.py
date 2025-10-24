"""
Author: Martin

Date: 2025-09-22

License: Unlicense

Description:
    File Manager, helps with file creation and management
"""

import json
from pathlib import Path
import pickle
from typing import List, Any
import logging


class FileManager:
    """
    Utility file functions
    """

    def __init__(self, directory: str, filename: str) -> None:
        """
        Initialize a FileManager object. Creates the directory if it doesn't exist.
        Logs actions performed by the instance.

        Args:
            directory (str): The directory where data will be stored and loaded.
                             Can be a relative or absolute path.
            filename (str): The name of the file to manage within the directory.
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.directory = Path(directory).resolve()
        if not self.directory.is_dir():
            self.logger.info(f"Created directory: {self.directory}")
        self.directory.mkdir(parents=True, exist_ok=True)
        self.filename = filename

    def __str__(self) -> str:
        return str((self.directory / self.filename))

    def exists(self) -> bool:
        """
        Check if a file exists.
        Logs the check.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        exists = (self.directory / self.filename).exists()
        self.logger.info(
            f"Checked if '{self.filename}' exists in '{self.directory}': {exists}"
        )
        return exists

    def delete_file(self):
        """
        Delete a file.
        Logs the deletion.

        Returns:
            None
        """
        filepath = self.directory / self.filename
        if filepath.exists():
            filepath.unlink()
            self.logger.info(f"Deleted file: {filepath}")
        else:
            self.logger.info(f"Attempted to delete non-existent file: {filepath}")

    def dump(self, data: Any, indent: int | str | None = None):
        """
        Dumps data to a json file.

         Returns:
            None
        """
        filepath = self.directory / self.filename
        with open(filepath, "w") as f:
            json.dump(data, f, indent=indent)
            self.logger.info(f"Wrote JSON data to: {filepath}")

    def load(self) -> Any:
        """
        Reads a json file and returns the data.

         Returns:
            list: The data from the json file.
        """
        filepath = self.directory / self.filename
        with open(filepath, "r") as f:
            data = json.load(f)
            self.logger.info(f"Read JSON data from: {filepath}")
            return data

    @staticmethod
    def delete_dir(relative_dir: str):
        """
        Deletes a directory and all of its contents.

        Parameters:
            directory (str): The name of the directory to delete.

        Returns:
            None
        """
        # Get a logger for the static method
        static_logger = logging.getLogger(f"{__name__}.FileManager")
        directory = Path(relative_dir).resolve()
        if directory.exists():
            for file in directory.iterdir():
                if file.is_file():
                    file.unlink()
                    static_logger.info(f"Deleted file during directory removal: {file}")
                elif file.is_dir():
                    FileManager.delete_dir(f"{relative_dir}/{file.name}")
            directory.rmdir()
            static_logger.info(f"Removed directory: {directory}")
