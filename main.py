import discord
from discord.ext import commands
import random
import os
from flask import Flask
from threading import Thread

# --- 1. SERVER WEB (Pentru a menține botul activ pe Render) ---
app = Flask('')

@app.route('/')
def home():
    return "Statia Radio este Online!"

def run():
    # Render folosește variabila PORT pentru serviciile web
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- 2. LOGICA BOTULUI DISCORD ---
intents = discord.Intents.default()
intents.message_content = True  # Necesar pentru a citi comanda !radio

bot = commands.Bot(command_prefix="!", intents=intents)

# Definim interfața cu buton
class RadioView(discord.ui.View):
    def __init__(self):
        # timeout=None asigură că butonul nu expiră după câteva minute
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Scanare Frecvență 📡", 
        style=discord.ButtonStyle.green, 
        custom_id="scan_btn_unique" # ID unic pentru persistență la restart
    )
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Generăm formatul abc.de (ex: 145.05)
        abc = random.randint(100, 999)
        de = random.randint(0, 99)
        frecventa = f"{abc}.{de:02d}" # :02d pune un 0 în față dacă cifra e mică
        
        await interaction.response.send_message(
            f"📟 **Sistem:** Frecvență interceptată pe **{frecventa} MHz**", 
            ephemeral=True # Mesajul este vizibil doar pentru cel care apasă
        )

@bot.event
async def on_ready():
    # Înregistrăm View-ul pentru ca butoanele vechi să rămână funcționale
    bot.add_view(RadioView())
    print(f'---')
    print(f'✅ Autentificat ca: {bot.user.name}')
    print(f'✅ ID Bot: {bot.user.id}')
    print(f'🚀 Botul este gata de utilizare!')
    print(f'---')

@bot.command()
async def radio(ctx):
    """Comanda care trimite panoul cu buton"""
    embed = discord.Embed(
        title="🛰️ Terminal Comunicații Radio",
        description="Apasă butonul de mai jos pentru a genera o frecvență random securizată.",
        color=0x2ecc71 # Verde smarald
    )
    embed.add_field(name="Protocol", value="Criptare AES-256", inline=True)
    embed.add_field(name="Status", value="📡 Scaner activ", inline=True)
    embed.set_footer(text="Sistem automat de alocare frecvențe.")
    
    await ctx.send(embed=embed, view=RadioView())

# --- 3. PORNIREA SISTEMULUI ---
if __name__ == "__main__":
    # Pornim serverul Flask într-un thread separat
    keep_alive()
    
    # Luăm Token-ul din variabilele de mediu (Environment Variables)
    token = os.environ.get('DISCORD_TOKEN')
    
    if token:
        try:
            bot.run(token)
        except discord.errors.LoginFailure:
            print("❌ EROARE: Token-ul Discord este invalid!")
        except Exception as e:
            print(f"❌ A apărut o eroare la pornire: {e}")
    else:
        print("❌ EROARE: Variabila 'DISCORD_TOKEN' nu a fost găsită!")
