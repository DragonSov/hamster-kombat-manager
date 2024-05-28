import logging
from os import path, makedirs, listdir
from telethon.sync import TelegramClient
from src.core.settings import settings

logger = logging.getLogger(__name__)


class SessionManager:
	"""
	Manages Telegram sessions including creation, listing, and deletion.
	"""

	def __init__(self):
		self.session_dir = settings.SESSION_DIRECTORY
		self.api_id = settings.API_ID
		self.api_hash = settings.API_HASH
		self._ensure_session_directory()

	def _ensure_session_directory(self):
		"""
		Ensure the session directory exists, create it if it doesn't.
		"""
		if not path.exists(self.session_dir):
			makedirs(self.session_dir)
			logger.info(f"Directory {self.session_dir} has been created.")
		else:
			logger.info(f"Directory {self.session_dir} already exists.")

	async def create_session(self, name: str) -> bool:
		"""
		Create a new Telegram session.

		Args:
			name (str): The name of the session to create.

		Returns:
			bool: True if the session was created successfully.
		"""
		session_path = f"{self.session_dir}/{name}"
		async with TelegramClient(session=session_path, api_id=self.api_id, api_hash=self.api_hash) as client:
			logger.info(f"Session {name} has been created.")
		return True

	def get_session_names(self) -> list[str]:
		"""
		Get the names of all existing sessions.

		Returns:
			list[str]: A list of session names.
		"""
		return [filename[:-8] for filename in listdir(self.session_dir) if filename.endswith(".session")]

	async def delete_session(self, name: str) -> bool:
		"""
		Delete an existing Telegram session.

		Args:
			name (str): The name of the session to delete.

		Returns:
			bool: True if the session was deleted successfully.
		"""
		session_path = f"{self.session_dir}/{name}"
		async with TelegramClient(session=session_path, api_id=self.api_id, api_hash=self.api_hash) as client:
			await client.log_out()
			logger.info(f"Session {name} has been deleted.")
		return True
