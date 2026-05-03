import sys
import os
import asyncio
from dotenv import load_dotenv

# --- Section 1: Environment & Path Setup ---
# Ensures Python 3.14 finds the correct libraries
LIB_PATH = r"C:\Users\Justin Choi\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages"
if LIB_PATH not in sys.path:
    sys.path.insert(0, LIB_PATH)

try:
    import discord
except ImportError:
    print("Error: discord.py-self not found.")
    sys.exit()

# Load credentials from your .env file
load_dotenv()
TOKEN_1 = os.getenv('TOKEN1', '').strip()
TOKEN_2 = os.getenv('TOKEN2', '').strip()
TARGET_CHANNEL_ID = int(os.getenv('TARGET_CHANNEL_ID', 0))

# Global state variables
is_running = False
current_number = 1
reset_triggered = False

# --- Section 2: Bot Client Logic ---
class CountingBot(discord.Client):
    def __init__(self, bot_name, *args, **kwargs):
        # self_bot=True is essential for user account automation
        super().__init__(self_bot=True, *args, **kwargs)
        self.bot_name = bot_name

    async def on_ready(self):
        print(f"[{self.bot_name}] Logged in as: {self.user}")

    async def on_message(self, message):
        global is_running, current_number, reset_triggered
        
        # Only respond in the designated channel
        if message.channel.id != TARGET_CHANNEL_ID:
            return

        # Command: !start or !start [number]
        if message.content.startswith("!start"):
            args = message.content.split()
            if len(args) > 1:
                try:
                    # Manually jump to a specific number
                    current_number = int(args[1])
                    print(f"[{self.bot_name}] Jumped to: {current_number}")
                except ValueError:
                    print(f"[{self.bot_name}] Invalid input. Continuing from {current_number}")
            
            if not is_running:
                is_running = True
                print(f"[{self.bot_name}] Counting: STARTED")
        
        # Command: !stop
        elif message.content == "!stop":
            is_running = False
            print(f"[{self.bot_name}] Counting: STOPPED")
            
        # Command: !reset
        elif message.content == "!reset":
            current_number = 1
            reset_triggered = True
            print(f"[{self.bot_name}] Global Counter: RESET TO 1")

# --- Section 3: Dual-Account Logic ---
bot1 = CountingBot(bot_name="Account_1")
bot2 = CountingBot(bot_name="Account_2")

async def run_counting_logic():
    global is_running, current_number, reset_triggered
    
    while True:
        if is_running:
            # Alternates between both bot accounts
            for active_bot in [bot1, bot2]:
                if not is_running or reset_triggered:
                    break
                
                channel = active_bot.get_channel(TARGET_CHANNEL_ID)
                if channel:
                    try:
                        await channel.send(str(current_number))
                        print(f"[{active_bot.bot_name}] Sent: {current_number}")
                        current_number += 1
                    except Exception as e:
                        print(f"[{active_bot.bot_name}] Error: {e}")
                
                # 0.5s delay as requested (Caution: Fast speed)
                await asyncio.sleep(0.5)
            
            if reset_triggered:
                reset_triggered = False
                continue
        else:
            # Low CPU usage when idle
            await asyncio.sleep(0.1)

# --- Section 4: Main Entry Point ---
async def main():
    print("Starting Multi-Account System...")
    if not TOKEN_1 or not TOKEN_2:
        print("Error: TOKEN1 or TOKEN2 is missing in .env")
        return

    # Run everything concurrently
    await asyncio.gather(
        bot1.start(TOKEN_1),
        bot2.start(TOKEN_2),
        run_counting_logic()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram closed by user.")
