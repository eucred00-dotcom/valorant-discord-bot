import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
from datetime import datetime

# ---------------- ENV ----------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ---------------- RANK ROLES ----------------
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

# ---------------- INTENTS ----------------
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

# ================= REGULI BUTTONS =================
class ReguliView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Caută jucători", style=discord.ButtonStyle.primary, emoji="🔍")
    async def cauta(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "🔍 Pentru a căuta jucători, folosește comanda:\n`/cauta`",
            ephemeral=True
        )

    @discord.ui.button(label="Creează squad", style=discord.ButtonStyle.success, emoji="👥")
    async def squad(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "👥 Pentru a crea un squad, folosește comanda:\n`/lfg`",
            ephemeral=True
        )

# ---------------- /REGULI ----------------
@bot.tree.command(name="reguli", description="Afișează regulile serverului Valorant România")
async def reguli(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📜 Valorant România",
        description=(
            "• Vă rugăm să nu căutați jucători pe **#general-chat** sau alte canale. "
            "Folosiți **#cauta-jucatori**, canal dedicat acestui scop.\n"
            "• Trimiterea linkurilor către alte servere Discord se sancționează cu **ban**.\n"
            "• Este interzisă folosirea cuvintelor rasiste, jignitoare sau ofensatoare.\n"
            "• Nu postați poze indecente, ciudate sau inadecvate.\n"
            "• Doxxing-ul (publicarea informațiilor personale ale altora) este strict interzis.\n"
            "• Accesul pe server este permis doar persoanelor cu vârsta minimă de **16 ani**.\n"
            "• Regulile se aplică și la poza de profil, status, descriere sau orice element vizibil pe cont.\n"
            "• Vânzarea sau cumpărarea de conturi Riot Games este interzisă.\n"
            "• În privat, șantajul, amenințările sau hărțuirea sunt sancționate dacă există dovezi clare.\n"
            "• Orice reclamație legată de voice chat trebuie susținută cu **dovadă video**.\n"
            "• Nu pretindeți că sunteți activi, membri obișnuiți sau staff.\n"
            "• Nu instigați la certuri sau conflicte între membri.\n"
            "• Este interzis orice conținut ilegal (pedofilie, zoofilie, necrofilie etc.).\n"
            "• Reclama personală se face doar în **#self-promote** sau prin boții noștri.\n"
            "• Nu deranjați utilizatorii pe voice prin sunete, zgomote sau muzică fără acord.\n"
            "• Discuțiile cu conținut sexual explicit sau violență grafică sunt interzise.\n"
            "• Subiectele politice nu sunt permise pe server.\n"
            "• Nu folosiți conturi alternative pentru a ocoli sancțiuni.\n"
            "• Respectați staff-ul și deciziile acestuia; discuțiile se fac prin **ticket**.\n"
            "• Nu spamați canalele cu mesaje repetitive, linkuri sau reacții abuzive.\n"
            "• Respectați regulile suplimentare afișate în descrierea canalelor.\n\n"
            "**Prin prezența pe acest server, sunteți de acord cu regulile de mai sus.**"
        ),
        color=0xff4655
    )

    embed.set_image(
        url="https://images.contentstack.io/v3/assets/bltb6530b271fddd0b1/bltced3c6b8caa1f4a3/63c9a2f13cdaef7a1f3ccf1c/VALORANT_EP6_Act1_KeyArt.jpg"
    )

    embed.set_footer(
        text="Nerespectarea regulilor poate duce la sancțiuni temporare sau permanente."
    )

    await interaction.response.send_message(embed=embed, view=ReguliView())

# ---------------- /RANK ----------------
@bot.tree.command(name="rank", description="Primești rol automat pe baza rankului")
async def rank(interaction: discord.Interaction, rank: str):
    rank = rank.lower()
    if rank not in RANK_ROLES:
        await interaction.response.send_message("❌ Rank invalid!", ephemeral=True)
        return

    role = discord.utils.get(interaction.guild.roles, name=RANK_ROLES[rank])
    if not role:
        await interaction.response.send_message("❌ Rolul nu există.", ephemeral=True)
        return

    for r in interaction.user.roles:
        if r.name in RANK_ROLES.values():
            await interaction.user.remove_roles(r)

    await interaction.user.add_roles(role)
    await interaction.response.send_message(
        embed=discord.Embed(
            title="🏆 Rank setat",
            description=f"Ai primit **{role.name}**",
            color=0xff4655
        )
    )

# ================= LFG NORMAL =================
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
            await interaction.response.send_message("❌ Echipa e completă.", ephemeral=True)
            return

        self.joined.append(interaction.user)
        await interaction.response.send_message("✅ Te-ai înscris!", ephemeral=True)

        if len(self.joined) == self.needed:
            await interaction.channel.send(
                "🔥 **ECHIPĂ COMPLETĂ!**\n" +
                ", ".join(u.mention for u in self.joined)
            )

@bot.tree.command(name="lfg", description="Caut echipă Valorant")
async def lfg(interaction: discord.Interaction, jucatori: int, rankuri: str, mod: str):
    embed = discord.Embed(
        title=f"🔊 Caut {jucatori} jucători!",
        color=0xff4655,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="🏆 Rank-uri", value=rankuri)
    embed.add_field(name="🎮 Mod", value=mod)
    embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed, view=LFGView(jucatori))

# ================= PREMIER LFG =================
class PremierLFGView(discord.ui.View):
    def __init__(self, needed):
        super().__init__(timeout=None)
        self.needed = needed
        self.joined = []

    @discord.ui.button(label="Join", style=discord.ButtonStyle.success, emoji="🎮")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.joined:
            await interaction.response.send_message("❌ Deja înscris.", ephemeral=True)
            return
        if len(self.joined) >= self.needed:
            await interaction.response.send_message("❌ Complet.", ephemeral=True)
            return

        self.joined.append(interaction.user)
        await interaction.response.send_message("✅ Înscris!", ephemeral=True)

@bot.tree.command(name="premier", description="LFG Premier")
async def premier(
    interaction: discord.Interaction,
    jucatori: int,
    rank_range: str,
    controllers: int,
    sentinels: int,
    subs: int,
    info: str
):
    embed = discord.Embed(
        title=f"Premier: Looking for {jucatori} players!",
        color=0xff4655,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="🏆 Rank range", value=rank_range, inline=False)
    embed.add_field(
        name="🎯 Agent roles needed",
        value=f"Controllers: {controllers}\nSentinels: {sentinels}",
        inline=False
    )
    embed.add_field(name="🔁 Subs needed", value=subs)
    embed.add_field(name="ℹ️ Additional info", value=info)
    embed.set_footer(text="Valorant România")
    await interaction.response.send_message(embed=embed, view=PremierLFGView(jucatori))

# ================= LFG PANEL =================
class LFGPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ranked", style=discord.ButtonStyle.danger)
    async def ranked(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Folosește `/lfg`", ephemeral=True)

    @discord.ui.button(label="Unrated", style=discord.ButtonStyle.success)
    async def unrated(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Folosește `/lfg`", ephemeral=True)

    @discord.ui.button(label="Altele", style=discord.ButtonStyle.primary)
    async def altele(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Folosește `/premier`", ephemeral=True)

@bot.tree.command(name="cauta", description="Panou căutare jucători")
async def cauta(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔎 Caută jucători!",
        description="Apasă pe un buton de mai jos pentru a începe!\n\n*Alternativ, poți folosi `/lfg`*",
        color=0x2b2d31
    )
    await interaction.response.send_message(embed=embed, view=LFGPanelView())

# ================= QUEUE =================
queue = []

@bot.tree.command(name="queue", description="Queue scrim 10 jucători")
async def queue_cmd(interaction: discord.Interaction):
    if interaction.user in queue:
        await interaction.response.send_message("❌ Deja în queue.", ephemeral=True)
        return
    queue.append(interaction.user)
    await interaction.response.send_message(f"✅ {interaction.user.mention} ({len(queue)}/10)")
    if len(queue) == 10:
        await interaction.channel.send("🔥 SCRIM COMPLET!\n" + ", ".join(p.mention for p in queue))
        queue.clear()

# ---------------- /ANUNT ----------------
@bot.tree.command(name="anunt", description="Anunț oficial")
async def anunt(interaction: discord.Interaction, mesaj: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Doar adminii.", ephemeral=True)
        return
    await interaction.response.send_message(
        embed=discord.Embed(title="📢 ANUNȚ", description=mesaj, color=0xff4655)
    )

# ---------------- RUN ----------------
bot.run(TOKEN)
