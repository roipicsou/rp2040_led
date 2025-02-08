import serial
import time
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Remplacez par le port série de votre carte (ex: "COM3" sous Windows, "/dev/ttyUSB0" sous Linux/macOS)
PORT = "COM5"
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
    print("le bot est un route")
    try :
        synced = await bot.tree.sync()
        print(f"Comande sincroniée : {len(synced)}")
    except Exception as e :
        print(e)

@bot.tree.command(name="led_on", description="alumme les led")
async def led_on(interaction : discord.Interaction) :
    send_command("ON")
    await interaction.response.send_message("led on")

@bot.tree.command(name="led_off", description="eteind les led")
async def led_off(interaction : discord.Interaction) :
    send_command("OFF")
    await interaction.response.send_message("led off")

@bot.tree.command(name="c_lum", description="changer l'intensitéer des led")
async def c_lum(interaction : discord.Interaction, lm: int) :
    send_command(f"C_LUM,{lm}")
    await interaction.response.send_message(f"la luminosiée est changer a {lm}")

bot.run(os.getenv('DISCORD'))