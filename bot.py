import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
from datetime import datetime

from ranks import RANK_ROLES

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

from ranks import RANK_ROLES
RANK_ROLES = {
    "iron": "Iron",
    "bronze": "Bronze",
    "silver": "Silver",
    "gold": "Gold",
    "platinum": "Platinum",
    "diamond": "Diamond",
    "ascendant": "Ascendant",
    "immortal": "Immortal",
    "radiant": "Radiant"
}


# ---------------- CONFIG ----------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- READY ----------------
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"🔥 Bot online: {bot.user}")

# ---------------- /PING ----------------
@bot.tree.command(name="ping", description="Test bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

# ---------------- /RANK ----------------
@bot.tree.command(name="rank", description="Primești rol automat pe baza rankului")
@app_commands.describe(rank="Iron, Bronze, Silver, Gold, Platinum, Diamond, Ascendant, Immortal, Radiant")
async def rank(interaction: discord.Interaction, rank: str):
    rank = rank.lower()

    if rank not in RANK_ROLES:
        await interaction.response.send_message("❌ Rank invalid!", ephemeral=True)
        return

    role_name = RANK_ROLES[rank]
    role = discord.utils.get(interaction.guild.roles, name=role_name)

    if not role:
        await interaction.response.send_message("❌ Rolul nu există pe server.", ephemeral=True)
        return

    for r in interaction.user.roles:
        if r.name in RANK_ROLES.values():
            await interaction.user.remove_roles(r)

    await interaction.user.add_roles(role)

    embed = discord.Embed(
        title="🏆 Rank setat!",
        description=f"Ai primit rolul **{role_name}**",
        color=0xff4655
    )
    await interaction.response.send_message(embed=embed)

# ================= LFG SYSTEM =================

class LFGView(discord.ui.View):
    def __init__(self, needed):
        super().__init__(timeout=None)
        self.needed = needed
        self.joined = []

    @discord.ui.button(label="Join", style=discord.ButtonStyle.success, emoji="🎮")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.joined:
            await interaction.response.send_message("❌ Ești deja înscris.", ephemeral=True)
            return

        if len(self.joined) >= self.needed:
            await interaction.response.send_message("❌ Echipa este completă.", ephemeral=True)
            return

        self.joined.append(interaction.user)
        await interaction.response.send_message("✅ Te-ai înscris!", ephemeral=True)

        if len(self.joined) == self.needed:
            players = ", ".join(u.mention for u in self.joined)
            await interaction.channel.send(
                f"🔥 **ECHIPĂ COMPLETĂ!**\n{players}"
            )

# ---------------- /LFG ----------------
@bot.tree.command(name="lfg", description="Caut echipă Valorant (embed stil oficial)")
@app_commands.describe(
    jucatori="Câți jucători cauți",
    rankuri="Ex: Gold – Platinum",
    mod="Ranked / Unrated / Premier"
)
async def lfg(interaction: discord.Interaction, jucatori: int, rankuri: str, mod: str):
    embed = discord.Embed(
        title=f"🔊 Caut {jucatori} jucători!",
        color=0xff4655,
        timestamp=datetime.utcnow()
    )

    embed.add_field(name="🏆 Rank-uri", value=rankuri, inline=True)
    embed.add_field(name="🎮 Mod de joc", value=mod, inline=True)

    embed.set_thumbnail(
        url="https://upload.wikimedia.org/wikipedia/commons/f/fc/Valorant_logo_-_pink_color_version.svg"
    )

    embed.set_footer(
        text=interaction.user.display_name,
        icon_url=interaction.user.display_avatar.url
    )

    view = LFGView(jucatori)
    await interaction.response.send_message(embed=embed, view=view)

# ================= QUEUE SCRIM =================
queue = []

@bot.tree.command(name="queue", description="Intră în queue de scrim (10 jucători)")
async def queue_cmd(interaction: discord.Interaction):
    if interaction.user in queue:
        await interaction.response.send_message("❌ Ești deja în queue.", ephemeral=True)
        return

    queue.append(interaction.user)
    await interaction.response.send_message(
        f"✅ {interaction.user.mention} a intrat în queue ({len(queue)}/10)"
    )

    if len(queue) == 10:
        players = ", ".join(p.mention for p in queue)
        await interaction.channel.send(f"🔥 **SCRIM COMPLET!**\n{players}")
        queue.clear()

# ---------------- /ANUNT ----------------
@bot.tree.command(name="anunt", description="Anunț oficial Valorant")
@app_commands.describe(mesaj="Mesajul anunțului")
async def anunt(interaction: discord.Interaction, mesaj: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Doar adminii pot folosi comanda.", ephemeral=True)
        return

    embed = discord.Embed(
        title="📢 ANUNȚ VALORANT",
        description=mesaj,
        color=0xff4655
    )
    await interaction.response.send_message(embed=embed)

# ---------------- RUN ----------------
bot.run(TOKEN)

