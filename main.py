import serial
import time
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Remplacez par le port série de votre Smart Pi One (ex: "/dev/ttyAMA0" sous Linux)
PORT = "/dev/ttyAMA0"
BAUDRATE = 9600
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
    print("Le bot est en ligne.")
    try:
        synced = await bot.tree.sync()
        print(f"Commandes synchronisées : {len(synced)}")
    except Exception as e:
        print(e)

@bot.tree.command(name="led_on", description="Allume les LEDs")
async def led_on(interaction: discord.Interaction):
    send_command("ON")
    await interaction.response.send_message("LED allumées")

@bot.tree.command(name="led_off", description="Éteint les LEDs")
async def led_off(interaction: discord.Interaction):
    send_command("OFF")
    await interaction.response.send_message("LED éteintes")

@bot.tree.command(name="c_lum", description="Changer l'intensité des LEDs")
async def c_lum(interaction: discord.Interaction, lm: int):
    send_command(f"C_LUM,{lm}")
    await interaction.response.send_message(f"L'intensité des LEDs est changée à {lm}")

bot.run(os.getenv('DISCORD'))