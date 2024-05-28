import asyncio
import random
import argparse
from telethon.sync import TelegramClient
from src.core import settings
from src.managers import SessionManager
from src.tapper import Tapper


def display_menu() -> None:
	"""
	Display the main menu for the HAMSTER BOT Manager.
	"""
	print(r"""
 _______ _______ _______ _______ _______ _______ ______ 
|   |   |   _   |   |   |     __|_     _|    ___|   __ \
|       |       |       |__     | |   | |    ___|      <
|___|___|___|___|__|_|__|_______| |___| |_______|___|__|
    """)
	print("Welcome to the HAMSTER BOT Manager")
	print("1) Create a new session")
	print("2) List all sessions")
	print("3) Delete a session")
	print("4) Run the bot for all sessions")
	print("5) Exit")


async def create_new_session(session_manager: SessionManager, name: str = None) -> None:
	"""
	Create a new session.

	Args:
		session_manager (SessionManager): The session manager.
		name (str): The name of the session to create.
	"""
	if not name:
		name = input("Enter the session name: ")
	await session_manager.create_session(name)
	print(f"Session '{name}' created successfully.")


def list_sessions(session_manager: SessionManager) -> None:
	"""
	List all sessions.

	Args:
		session_manager (SessionManager): The session manager.
	"""
	sessions = session_manager.get_session_names()
	if not sessions:
		print("No sessions found.")
	else:
		print("Available sessions:")
		for session in sessions:
			print(f" - {session}")


async def delete_session(session_manager: SessionManager, name: str = None) -> None:
	"""
	Delete a session.

	Args:
		session_manager (SessionManager): The session manager.
		name (str): The name of the session to delete.
	"""
	list_sessions(session_manager)
	if not name:
		name = input("Enter the session name to delete: ")
	await session_manager.delete_session(name)
	print(f"Session '{name}' deleted successfully.")


async def run_tapper(session_name: str) -> None:
	"""
	Run the tapper bot for a specific session.

	Args:
		session_name (str): The name of the session.
	"""
	session_path = f"{settings.SESSION_DIRECTORY}/{session_name}"
	async with TelegramClient(session=session_path, api_id=settings.API_ID, api_hash=settings.API_HASH) as client:
		tapper = Tapper(client, session_name)
		try:
			web_data = await tapper.get_web_data()
			token = await tapper.login(web_data)
			if token is None:
				raise Exception("Login failed.")

			while True:
				try:
					profile = await tapper.get_profile_data(token)
					if profile is None:
						print(f"{session_name}: Profile data is None. Retrying...")
						await asyncio.sleep(settings.RETRY_DELAY)
						continue

					display_profile_info(profile, session_name)

					if settings.AUTO_UPGRADE:
						await process_upgrades(tapper, token, profile, session_name)

					tasks = await tapper.get_tasks(token)

					daily_task = next(task for task in tasks if task["id"] == "streak_days")

					if not daily_task["isCompleted"]:
						await tapper.check_task(token, daily_task["id"])
						reward = daily_task["rewardCoins"]
						days = daily_task["days"]

						print(f"{session_name}: Completed daily task for {days} days. Reward: {reward}")

					await process_taps(tapper, token, profile, session_name)
				except Exception as e:
					print(f"{session_name}: Error in tapping loop: {e}")
					raise
		except Exception as e:
			print(f"{session_name}: Error in main process: {e}")
			raise


def display_profile_info(profile: dict, session_name: str) -> None:
	"""
	Display specific information from the profile.

	Args:
		profile (dict): The profile data.
		session_name (str): The name of the session.
	"""
	earn_passive_per_sec = profile.get("earnPassivePerSec", 0)
	earn_passive_per_hour = profile.get("earnPassivePerHour", 0)
	last_passive_earn = profile.get("lastPassiveEarn", 0)
	balance_coins = profile.get("balanceCoins", 0)
	total_coins = profile.get("totalCoins", 0)

	print(f"{session_name}: Passive Earnings - {earn_passive_per_sec} per sec, {earn_passive_per_hour} per hour.")
	print(
		f"{session_name}: Last Passive Earn: {last_passive_earn}, Balance Coins: {balance_coins}, Total Coins: {total_coins}")


async def process_upgrades(tapper: Tapper, token: str, profile: dict, session_name: str) -> None:
	"""
	Process upgrades for the tapper bot.

	Args:
		tapper (Tapper): The tapper instance.
		token (str): The access token.
		profile (dict): The profile data.
		session_name (str): The name of the session.
	"""

	async def is_upgrade_eligible(upgrade: dict) -> bool:
		return (
				upgrade["level"] < settings.MAX_LEVEL_UPGRADE
				and (upgrade["level"] - 1) != upgrade.get("maxLevel", -1)
				and upgrade.get("cooldownSeconds", 0) == 0
		)

	upgrades = await tapper.get_upgrades_for_buy(token)
	if upgrades is None:
		print(f"{session_name}: Upgrades data is None. Skipping upgrade process.")
		return

	available_upgrades = [
		upgrade for upgrade in upgrades
		if upgrade["isAvailable"] and not upgrade["isExpired"]
	]

	upgrade_priority = {
		upgrade["id"]: upgrade["profitPerHourDelta"] / upgrade["price"]
		for upgrade in available_upgrades
		if await is_upgrade_eligible(upgrade)
	}

	sorted_upgrades = sorted(upgrade_priority.items(), key=lambda item: item[1], reverse=True)

	for upgrade_id, _ in sorted_upgrades:
		price = next(upgrade["price"] for upgrade in upgrades if upgrade["id"] == upgrade_id)
		if price > profile["balanceCoins"]:
			print(
				f"{session_name}: Not enough coins to purchase upgrade {upgrade_id}. Required: {price}, Current: {profile['balanceCoins']}. Accumulating coins...")
			return
		else:
			profit_per_hour_delta = next(
				upgrade["profitPerHourDelta"] for upgrade in upgrades if upgrade["id"] == upgrade_id)
			payback_period = price / profit_per_hour_delta if profit_per_hour_delta > 0 else float('inf')

			await tapper.buy_upgrade(token, upgrade_id)
			profile["balanceCoins"] -= price
			print(
				f"{session_name}: Purchased upgrade {upgrade_id} for {price} coins. Payback period: {payback_period:.2f} hours.")


async def process_taps(tapper: Tapper, token: str, profile: dict, session_name: str) -> None:
	"""
	Process taps for the tapper bot.

	Args:
		tapper (Tapper): The tapper instance.
		token (str): The access token.
		profile (dict): The profile data.
		session_name (str): The name of the session.
	"""
	available_energy = profile.get("availableTaps", 0)
	boosts = await tapper.get_boosts_for_buy(token)
	if boosts is None:
		print(f"{session_name}: Boosts data is None. Skipping boosts process.")
		return

	for boost in boosts:
		if boost["price"] <= profile["balanceCoins"] and boost["level"] < settings.MAX_LEVEL_BOOST and boost[
			"id"] != "BoostFullAvailableTaps":
			await tapper.buy_boost(token, boost["id"])
			profile["balanceCoins"] -= boost["price"]

	energy_boost = [boost for boost in boosts if boost["id"] == "BoostFullAvailableTaps"][0]

	if available_energy < settings.MIN_AVAILABLE_ENERGY:
		if settings.APPLY_DAILY_ENERGY and energy_boost and energy_boost["cooldownSeconds"] == 0 and energy_boost[
			"level"] <= energy_boost["maxLevel"]:
			if await tapper.buy_boost(token, "BoostFullAvailableTaps"):
				print(f"{session_name}: Energy boost activated.")
				return

		sleep_time = random.randint(*settings.SEND_TAPS_WAIT)
		print(f"{session_name}: Not enough energy. Waiting for {sleep_time} seconds.")
		await asyncio.sleep(sleep_time)

		cooldown_time = random.randint(*settings.SEND_TAPS_COOLDOWN)
		print(f"{session_name}: Cooling down for {cooldown_time} seconds.")
		await asyncio.sleep(cooldown_time)

	else:
		taps_count = random.randint(*settings.SEND_TAPS_COUNT)
		profile = await tapper.send_taps(
			access_token=token,
			available_energy=available_energy,
			taps=taps_count,
		)
		if profile is None:
			print(f"{session_name}: Taps data is None. Skipping taps process.")
			return

		print(f"{session_name}: Sent {taps_count} taps. Updated profile:")
		display_profile_info(profile, session_name)


async def run_tapper_with_retries(session_name: str) -> None:
	"""
	Run the tapper bot with retries for a specific session.

	Args:
		session_name (str): The name of the session.
	"""
	for attempt in range(settings.MAX_RETRIES):
		try:
			await run_tapper(session_name)
			return
		except Exception as e:
			print(f"{session_name}: Attempt {attempt + 1}/{settings.MAX_RETRIES} failed with error: {e}")
			if attempt < settings.MAX_RETRIES - 1:
				print(f"{session_name}: Retrying in {settings.RETRY_DELAY} seconds...")
				await asyncio.sleep(settings.RETRY_DELAY)
			else:
				print(f"{session_name}: All retry attempts failed.")
				raise


async def run_bot_for_all_sessions(session_manager: SessionManager) -> None:
	"""
	Run the bot for all sessions.

	Args:
		session_manager (SessionManager): The session manager.
	"""
	sessions = session_manager.get_session_names()
	if not sessions:
		print("No sessions found.")
		return

	await asyncio.gather(*(run_tapper_with_retries(session) for session in sessions))


async def main() -> None:
	"""
	The main function to run the HAMSTER BOT Manager.
	"""
	parser = argparse.ArgumentParser(description="HAMSTER BOT Manager")
	parser.add_argument("--create-session", type=str, help="Create a new session with the given name")
	parser.add_argument("--list-sessions", action="store_true", help="List all sessions")
	parser.add_argument("--delete-session", type=str, help="Delete the session with the given name")
	parser.add_argument("--run-bot", action="store_true", help="Run the bot for all sessions")
	args = parser.parse_args()

	session_manager = SessionManager()

	if args.create_session:
		await create_new_session(session_manager, args.create_session)
	elif args.list_sessions:
		list_sessions(session_manager)
	elif args.delete_session:
		await delete_session(session_manager, args.delete_session)
	elif args.run_bot:
		await run_bot_for_all_sessions(session_manager)
	else:
		while True:
			display_menu()
			choice = input("Enter your choice: ")
			if choice == '1':
				await create_new_session(session_manager)
			elif choice == '2':
				list_sessions(session_manager)
			elif choice == '3':
				await delete_session(session_manager)
			elif choice == '4':
				await run_bot_for_all_sessions(session_manager)
			elif choice == '5':
				print("Exiting...")
				break
			else:
				print("Invalid choice, please try again.")


if __name__ == "__main__":
	asyncio.run(main())
