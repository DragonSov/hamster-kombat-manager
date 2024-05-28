import logging
import time
from aiohttp import ClientSession
from telethon import functions
from urllib.parse import unquote

logger = logging.getLogger(__name__)


class Tapper:
	def __init__(self, tg_client, session_name: str):
		"""
		Initialize the Tapper class with a Telegram client and session name.

		Args:
			tg_client (TelegramClient): The Telegram client instance.
			session_name (str): The name of the session.
		"""
		self.tg_client = tg_client
		self.session_name = session_name

	async def _connect_if_needed(self) -> None:
		"""
		Connect to the Telegram client if not already connected.
		"""
		if not self.tg_client.is_connected():
			await self.tg_client.connect()
			logger.debug(f"{self.session_name}: Telegram client connected.")

	async def _disconnect_if_needed(self) -> None:
		"""
		Disconnect from the Telegram client if connected.
		"""
		if self.tg_client.is_connected():
			await self.tg_client.disconnect()
			logger.debug(f"{self.session_name}: Telegram client disconnected.")

	async def get_web_data(self) -> str:
		"""
		Retrieve web data from the bot's web view.

		Returns:
			str: The extracted web data.
		"""
		await self._connect_if_needed()
		await self.tg_client.get_dialogs()
		bot_entity = await self.tg_client.get_entity(7018368922)
		result = await self.tg_client(functions.messages.RequestWebViewRequest(
			peer=bot_entity,
			bot=bot_entity,
			platform="android",
			from_bot_menu=False,
			url="https://hamsterkombat.io/",
			start_param="kentId770247847",
		))
		web_data = unquote(
			string=unquote(
				string=result.url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0],
			),
		)
		return web_data

	async def _make_request(self, url: str, data: dict = None, headers: dict = None) -> dict | None:
		"""
		Make an HTTP POST request to the specified URL with optional data and headers.

		Args:
			url (str): The URL to send the request to.
			data (dict, optional): The JSON data to include in the request.
			headers (dict, optional): The headers to include in the request.

		Returns:
			dict | None: The JSON response data or None if the request failed.
		"""
		async with ClientSession(headers=headers) as http_client:
			res = await http_client.post(url, json=data)
			if res.status != 200 and res.status != 422:
				print(f"{self.session_name}: Request failed with status {res.status}.")
				print(f"{self.session_name}: Response: {await res.text()}")
				return None
			if res.status == 422:
				print(f"{self.session_name}: Received 422 status code. Treating as valid response.")
			data = await res.json(content_type=None)
			return data

	async def login(self, web_data: str) -> str | None:
		"""
		Log in to the service using the provided web data.

		Args:
			web_data (str): The web data for authentication.

		Returns:
			str | None: The authentication token or None if login failed.
		"""
		data = {
			"initDataRaw": web_data,
			"fingerprint": {},
		}
		url = "https://api.hamsterkombat.io/auth/auth-by-telegram-webapp"
		response_data = await self._make_request(url, data)
		if response_data:
			return response_data["authToken"]
		return None

	async def get_profile_data(self, access_token: str) -> dict | None:
		"""
		Retrieve profile data for the user.

		Args:
			access_token (str): The access token for authentication.

		Returns:
			dict | None: The user's profile data or None if the request failed.
		"""
		headers = {"Authorization": f"Bearer {access_token}"}
		url = "https://api.hamsterkombat.io/clicker/sync"
		response_data = await self._make_request(url, headers=headers)
		if response_data:
			return response_data["found"]["clickerUser"] if response_data.get("type") == "validation" else \
				response_data["clickerUser"]
		return None

	async def get_boosts_for_buy(self, access_token: str) -> list | None:
		"""
		Retrieve a list of available boosts for purchase.

		Args:
			access_token (str): The access token for authentication.

		Returns:
			list | None: A list of boosts available for purchase or None if the request failed.
		"""
		headers = {"Authorization": f"Bearer {access_token}"}
		url = "https://api.hamsterkombat.io/clicker/boosts-for-buy"
		response_data = await self._make_request(url, headers=headers)
		if response_data:
			return response_data["found"]["boostsForBuy"] if response_data.get("type") == "validation" else \
				response_data["boostsForBuy"]
		return None

	async def get_upgrades_for_buy(self, access_token: str) -> list | None:
		"""
		Retrieve a list of available upgrades for purchase.

		Args:
			access_token (str): The access token for authentication.

		Returns:
			list | None: A list of upgrades available for purchase or None if the request failed.
		"""
		headers = {"Authorization": f"Bearer {access_token}"}
		url = "https://api.hamsterkombat.io/clicker/upgrades-for-buy"
		response_data = await self._make_request(url, headers=headers)
		if response_data:
			return response_data["found"]["upgradesForBuy"] if response_data.get("type") == "validation" else \
				response_data["upgradesForBuy"]
		return None

	async def get_tasks(self, access_token: str) -> list | None:
		"""
		Retrieve a list of available tasks.

		Args:
			access_token (str): The access token for authentication.

		Returns:
			list | None: A list of available tasks or None if the request failed.
		"""
		headers = {"Authorization": f"Bearer {access_token}"}
		url = "https://api.hamsterkombat.io/clicker/list-tasks"
		response_data = await self._make_request(url, headers=headers)
		if response_data:
			return response_data["found"]["tasks"] if response_data.get("type") == "validation" else \
				response_data["tasks"]
		return None

	async def send_taps(self, access_token: str, available_energy: int, taps: int) -> dict | None:
		"""
		Send taps to the service.

		Args:
			access_token (str): The access token for authentication.
			available_energy (int): The amount of available energy.
			taps (int): The number of taps to send.

		Returns:
			dict | None: The updated profile data after sending taps or None if the request failed.
		"""
		headers = {"Authorization": f"Bearer {access_token}"}
		data = {
			"availableTaps": available_energy,
			"count": taps,
			"timestamp": time.time(),
		}
		url = "https://api.hamsterkombat.io/clicker/tap"
		response_data = await self._make_request(url, data, headers=headers)
		if response_data:
			return response_data["found"]["clickerUser"] if response_data.get("type") == "validation" else \
				response_data["clickerUser"]
		return None

	async def buy_boost(self, access_token: str, boost_id: str) -> bool:
		"""
		Purchase a boost.

		Args:
			access_token (str): The access token for authentication.
			boost_id (str): The ID of the boost to purchase.

		Returns:
			bool: True if the purchase was successful, False otherwise.
		"""
		headers = {"Authorization": f"Bearer {access_token}"}
		data = {
			"boostId": boost_id,
			"timestamp": time.time(),
		}
		url = "https://api.hamsterkombat.io/clicker/buy-boost"
		response_data = await self._make_request(url, data, headers=headers)
		return bool(response_data)

	async def buy_upgrade(self, access_token: str, upgrade_id: str) -> bool:
		"""
		Purchase an upgrade.

		Args:
			access_token (str): The access token for authentication.
			upgrade_id (str): The ID of the upgrade to purchase.

		Returns:
			bool: True if the purchase was successful, False otherwise.
		"""
		headers = {"Authorization": f"Bearer {access_token}"}
		data = {
			"upgradeId": upgrade_id,
			"timestamp": time.time(),
		}
		url = "https://api.hamsterkombat.io/clicker/buy-upgrade"
		response_data = await self._make_request(url, data, headers=headers)
		return bool(response_data)

	async def check_task(self, access_token: str, task_id: str) -> bool:
		"""
		Check a task.

		Args:
			access_token (str): The access token for authentication.
			task_id (str): The ID of the task to check.

		Returns:
			bool: True if the task check was successful, False otherwise.
		"""
		headers = {"Authorization": f"Bearer {access_token}"}
		data = {
			"taskId": task_id,
		}
		url = "https://api.hamsterkombat.io/clicker/check-task"
		response_data = await self._make_request(url, data, headers=headers)
		return bool(response_data)
