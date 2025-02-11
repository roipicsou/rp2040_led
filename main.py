import serial
import time
import discord
from discord.ext import commands, tasks
import datetime
import psutil
from dotenv import load_dotenv
import os
import ast

# Remplacez par le port série de votre carte (ex: "COM3" sous Windows, "/dev/ttyUSB0" sous Linux/macOS)
PORT = "COM5" # "/dev/ttyACM0"
BAUDRATE = 9600
CHANNEL_ID = 1338257927047217202
load_dotenv()
nc = 0
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

try:
    # Ouvrir la connexion série
    ser = serial.Serial(PORT, BAUDRATE, timeout=1)
    time.sleep(2)
except serial.SerialException:
    print(f"Impossible d'ouvrir le port {PORT}. Vérifiez la connexion de votre carte.")
except KeyboardInterrupt:
    print("\nProgramme interrompu par l'utilisateur.")
    ser.close()

def send_command(command):
    nc += 1
    ser.write((command + "\n").encode())
    time.sleep(0.1)
    response = ser.readlines()
    for line in response:
        print(line.decode().strip())

@bot.event
async def on_ready():
    print("Le bot est en route")
    print("Heure actuelle du serveur :", datetime.datetime.now())
    print("Salon cible :", bot.get_channel(CHANNEL_ID))
    try:
        synced = await bot.tree.sync()
        print(f"Commandes synchronisées : {len(synced)}")
    except Exception as e:
        print(e)
    send_daily_message.start()

@bot.tree.command(name="led_on", description="Allume les LED")
async def led_on(interaction: discord.Interaction):
    send_command("ON")
    await interaction.response.send_message("LED allumées")

@bot.tree.command(name="led_off", description="Éteint les LED")
async def led_off(interaction: discord.Interaction):
    send_command("OFF")
    await interaction.response.send_message("LED éteintes")

@bot.tree.command(name="c_lum", description="Changer l'intensité des LED")
async def c_lum(interaction: discord.Interaction, lm: int):
    send_command(f"C_LUM,{lm}")
    await interaction.response.send_message(f"Luminosité changée à {lm}")

@bot.tree.command(name="c_max_lum", description="Changer l'intensité max des LED")
async def c_max_lum(interaction: discord.Interaction, max: int):
    send_command(f"C_LUM,{max}")
    await interaction.response.send_message(f"Luminosité max changée à {max}")

@bot.tree.command(name="set_color", description="Change la couleur des LED")
async def set_color(interaction: discord.Interaction):
    reactions = {"🔴": "255,0,0", "🟢": "0,255,0", "🔵": "0,0,255", "⚪": "255,255,255", "🇫🇷": "patriot"}
    await interaction.response.send_message("Choisissez une couleur :", ephemeral=False)
    message = await interaction.original_response()
    for reaction in reactions.keys():
        await message.add_reaction(reaction)
    
    def check(reaction, user):
        return user != bot.user and reaction.message.id == message.id and str(reaction.emoji) in reactions
    
    reaction, user = await bot.wait_for("reaction_add", check=check)
    color_value = reactions[str(reaction.emoji)]
    send_command("PATRIOT" if color_value == "patriot" else f"SET_COLOR,{color_value}")
    await interaction.followup.send(f"Couleur changée en {reaction} !")

@tasks.loop(time=datetime.time(hour=18, minute=0, second=0))
async def send_daily_message():
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        system_info = get_system_info()
        await channel.send(system_info)
        nc = 0
    else:
        print("Erreur : Impossible de trouver le salon.")

def get_system_info():
    # Récupération de la température CPU
    temp_data = psutil.sensors_temperatures()
    try:
        if "cpu_thermal" in temp_data and temp_data["cpu_thermal"]:
            valeur_current = temp_data["cpu_thermal"][0].current
            temperature = round(valeur_current, 2)
        else:
            temperature = "N/A"
    except Exception as e:
        print(f"Erreur lors de la récupération de la température : {e}")
        temperature = "N/A"

    # Récupération de l'utilisation de la RAM
    ram = psutil.virtual_memory()
    ram_usage = f"{ram.used / (1024 ** 2):.2f} MB / {ram.total / (1024 ** 2):.2f} MB ({ram.percent}%)"

    # Récupération de l'utilisation du stockage
    disk = psutil.disk_usage("/")
    storage_usage = f"{disk.used / (1024 ** 3):.2f} GB / {disk.total / (1024 ** 3):.2f} GB ({disk.percent}%)"

    # Récupération du temps de fonctionnement (uptime)
    uptime = os.popen("uptime -p").read().strip()

    return f"""
📊 **Statistiques du Smart Pi One** 📊
- 🌡 Température CPU : {temperature}°C
- 💾 RAM utilisée : {ram_usage}
- 🗄 Stockage utilisé : {storage_usage}
- ⏳ Uptime : {uptime}
- 🗄 nombre de comande passer {nc}
"""

bot.run(os.getenv('DISCORD'))