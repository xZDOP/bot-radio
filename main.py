import discord
from discord.ext import commands
import random
import os
from flask import Flask
from threading import Thread

# --- SERVER PENTRU GĂZDUIRE ---
app = Flask('')

@app.route('/')
def home():
    return "Statia Radio este Online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- LOGICA BOTULUI ---
intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

class RadioView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Scanare Frecvență 📡", style=discord.ButtonStyle.green, custom_id="scan_btn")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Format abc.de (ex: 446.05)
        abc = random.randint(100, 999)
        de = random.randint(0, 99)
        frecventa = f"{abc}.{de:02d}"
        
        await interaction.response.send_message(
            f"📟 **Sistem:** Frecvență interceptată pe **{frecventa} MHz**", 
            ephemeral=True
        )

@bot.event
async def on_ready():
    print(f'Suntem live ca: {bot.user}')

@bot.command()
async def radio(ctx):
    embed = discord.Embed(
        title="🛰️ Terminal Comunicații Radio",
        description="Apasă butonul de mai jos pentru a genera o frecvență random.",
        color=0x2ecc71
    )
    await ctx.send(embed=embed, view=RadioView())

if __name__ == "__main__":
    keep_alive()
    token = os.environ.get('DISCORD_TOKEN')
    bot.run(token)
