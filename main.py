import serial
import time
import discord
from discord.ext import commands, tasks
import datetime
import psutil
from dotenv import load_dotenv
import os

# Remplacez par le port série de votre carte (ex: "COM3" sous Windows, "/dev/ttyUSB0" sous Linux/macOS)
PORT = "COM5" # "/dev/ttyACM0"
BAUDRATE = 9600
CHANNEL_ID = 1338257927047217202
load_dotenv()
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
    ser.write((command + "\n").encode())
    time.sleep(0.1)
    response = ser.readlines()
    for line in response:
        print(line.decode().strip())

@bot.event
async def on_ready():
    print("Le bot est en route")
    try:
        synced = await bot.tree.sync()
        print(f"Commandes synchronisées : {len(synced)}")
    except Exception as e:
        print(e)

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

bot.run(os.getenv('DISCORD'))