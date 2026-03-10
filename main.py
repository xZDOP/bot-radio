import discord
from discord.ext import commands
import random
import os
import asyncio
from flask import Flask
from threading import Thread

# --- SERVER WEB (Keep-Alive) ---
app = Flask('')

@app.route('/')
def home():
    return "Statia Radio este Online!"

def run():
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)

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
        # Dicționar pentru a salva timpul ultimei apăsări pentru fiecare utilizator
        self.cooldowns = {}

    @discord.ui.button(
        label="Scanare Frecvență 📡", 
        style=discord.ButtonStyle.green, 
        custom_id="radio_scan_button_v1"
    )
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        now = asyncio.get_event_loop().time()
        
        # Verificăm dacă utilizatorul este în cooldown (30 secunde)
        if user_id in self.cooldowns and now - self.cooldowns[user_id] < 30:
            retry_after = int(30 - (now - self.cooldowns[user_id]))
            return await interaction.response.send_message(
                f"⚠️ **Sistem supraîncălzit!** Reîncercare posibilă în `{retry_after}s`.", 
                ephemeral=True
            )

        # Actualizăm timpul pentru cooldown
        self.cooldowns[user_id] = now
        
        # Generăm frecvența
        abc = random.randint(100, 999)
        de = random.randint(0, 99)
        frecventa = f"{abc}.{de:02d}"
        
        # Trimitem mesajul public
        await interaction.response.send_message(
            f"📟 **Sistem:** Frecvență interceptată pe **{frecventa} MHz**\n*(Acest mesaj se va auto-distruge în 2 minute)*", 
            ephemeral=False 
        )
        
        # Gestionăm auto-ștergerea (2 minute)
        msg = await interaction.original_response()
        await asyncio.sleep(120)
        
        try:
            await msg.delete()
        except:
            pass

@bot.event
async def on_ready():
    bot.add_view(RadioView())
    print(f'✅ Bot Online: {bot.user}')

@bot.command()
async def radio(ctx):
    embed = discord.Embed(
        title="🛰️ Terminal Comunicații Radio",
        description="Apasă butonul de mai jos pentru a genera o frecvență aleatorie.",
        color=0x2ecc71
    )
    embed.add_field(name="🛡️ Securitate", value="Auto-distrugere: 120s", inline=True)
    embed.add_field(name="⏳ Cooldown", value="30s per utilizator", inline=True)
    embed.set_footer(text="Velkaris Network System")
    
    await ctx.send(embed=embed, view=RadioView())

if __name__ == "__main__":
    keep_alive()
    token = os.environ.get('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ EROARE: Lipsă TOKEN!")
