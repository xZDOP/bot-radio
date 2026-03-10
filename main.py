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
        self.cooldowns = {}
        # Variabilă pentru a memora ultimul mesaj cu frecvența
        self.last_message = None

    @discord.ui.button(
        label="Scanare Frecvență 📡", 
        style=discord.ButtonStyle.green, 
        custom_id="radio_scan_button_v1"
    )
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        now = asyncio.get_event_loop().time()
        
        # Cooldown 30 secunde
        if user_id in self.cooldowns and now - self.cooldowns[user_id] < 30:
            retry_after = int(30 - (now - self.cooldowns[user_id]))
            return await interaction.response.send_message(
                f"⚠️ **Sistem supraîncălzit!** Reîncercare în `{retry_after}s`.", 
                ephemeral=True
            )

        # Ștergem mesajul anterior dacă acesta există
        if self.last_message:
            try:
                await self.last_message.delete()
            except:
                # Mesajul a fost probabil șters manual sau nu mai există
                pass

        self.cooldowns[user_id] = now
        
        abc = random.randint(100, 999)
        de = random.randint(0, 99)
        frecventa = f"{abc}.{de:02d}"
        
        # Trimitem noua frecvență
        await interaction.response.send_message(
            f"📟 **Sistem:** Frecvență interceptată pe **{frecventa} MHz**\n*(Acest mesaj va fi înlocuit la următoarea scanare)*", 
            ephemeral=False 
        )
        
        # Salvăm acest mesaj ca fiind cel mai nou
        self.last_message = await interaction.original_response()

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
    embed.add_field(name="🛡️ Mod Operare", value="O singură frecvență activă", inline=True)
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
