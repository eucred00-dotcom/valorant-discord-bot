import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
from datetime import datetime

# ---------------- ENV ----------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ---------------- INTENTS ----------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- READY ----------------
@bot.event
async def on_ready():
    bot.add_view(CautaView())
    bot.add_view(ReguliView())

    await bot.tree.sync()
    print(f"🔥 Bot online: {bot.user}")

# ---------------- /PING ----------------
@bot.tree.command(name="ping", description="Test bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

# ================= REGULI VIEW =================
class ReguliView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Caută jucători", style=discord.ButtonStyle.primary, emoji="🔍")
    async def cauta(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "🔍 Deschide panoul de căutare jucători:",
            view=CautaView(),
            ephemeral=True
        )

    @discord.ui.button(label="Creează squad", style=discord.ButtonStyle.success, emoji="👥")
    async def squad(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(LFGModal("Ranked"))

# ---------------- /REGULI ----------------
@bot.tree.command(name="reguli", description="Regulamentul Valorant România")
async def reguli(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📜 VALORANT ROMÂNIA — REGULAMENT",
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

    embed.set_footer(text="Sancțiuni temporare sau permanente")

    await interaction.response.send_message(embed=embed, view=ReguliView())

# ================= LFG VIEW =================
class LFGView(discord.ui.View):
    def __init__(self, needed: int, owner: discord.Member):
        super().__init__(timeout=None)
        self.needed = needed
        self.owner = owner
        self.joined = []

    @discord.ui.button(label="Join", style=discord.ButtonStyle.success, emoji="🎮")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):

        # dacă nu e în voice creatorul
        if not self.owner.voice or not self.owner.voice.channel:
            return await interaction.response.send_message(
                "❌ Creatorul squadului nu este într-un voice channel.",
                ephemeral=True
            )

        # dacă e deja înscris
        if interaction.user in self.joined:
            return await interaction.response.defer()  # NU trimite mesaj

        # dacă e plin
        if len(self.joined) >= self.needed:
            return await interaction.response.send_message(
                "❌ Squad complet.",
                ephemeral=True
            )

        # adăugăm jucătorul
        self.joined.append(interaction.user)

        # mutăm userul în voice-ul creatorului
        try:
            await interaction.user.move_to(self.owner.voice.channel)
        except discord.Forbidden:
            return await interaction.response.send_message(
                "❌ Nu am permisiunea să te mut în voice.",
                ephemeral=True
            )

        # NU trimitem niciun mesaj
        await interaction.response.defer()

        # dacă e complet
        if len(self.joined) == self.needed:
            await interaction.channel.send(
                "🔥 **ECHIPĂ COMPLETĂ!**\n" +
                ", ".join(u.mention for u in self.joined)
            )

# ================= LFG JOIN =================
class LFGJoinView(discord.ui.View):
    def __init__(self, owner: discord.Member, needed: int):
        super().__init__(timeout=None)
        self.owner = owner
        self.needed = needed
        self.joined = []

    @discord.ui.button(label="Join", style=discord.ButtonStyle.success, emoji="🎮")
    async def join(self, interaction: discord.Interaction, _):
        if interaction.user in self.joined:
            return

        self.joined.append(interaction.user)

        if self.owner.voice:
            await interaction.user.move_to(self.owner.voice.channel)

        if len(self.joined) >= self.needed:
            await interaction.channel.send(
                "🔥 **ECHIPĂ COMPLETĂ!**\n" +
                ", ".join(u.mention for u in self.joined)
            )

# ================= LFG MODAL =================
class LFGModal(discord.ui.Modal, title="LFG Ranked"):
    jucatori = discord.ui.TextInput(label="Câți jucători cauți?")
    rank_range = discord.ui.TextInput(label="Rank range (ex: Gold - Platinum)")
    mod = discord.ui.TextInput(label="Mod de joc", default="Ranked")

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"🔊 Caut {self.jucatori.value} jucători!",
            color=0xff4655,
            timestamp=datetime.utcnow()
        )

        embed.add_field(name="🏆 Rank range", value=self.rank_range.value, inline=False)
        embed.add_field(name="🎮 Mod", value=self.mod.value, inline=False)
        embed.set_footer(
            text=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url
        )

        view = LFGJoinView(interaction.user, int(self.jucatori.value))
        await interaction.response.send_message(embed=embed, view=view)

# ================= CAUTA VIEW =================
class CautaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ranked", style=discord.ButtonStyle.danger)
    async def ranked(self, interaction: discord.Interaction, _):
        await interaction.response.send_modal(LFGModal())

    @discord.ui.button(label="Unrated", style=discord.ButtonStyle.success)
    async def unrated(self, interaction: discord.Interaction, _):
        await interaction.response.send_modal(LFGModal())

    @discord.ui.button(label="Altele", style=discord.ButtonStyle.primary)
    async def altele(self, interaction: discord.Interaction, _):
        await interaction.response.send_modal(LFGModal())

@bot.tree.command(name="cauta", description="Caută jucători Valorant")
async def cauta(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔍 Caută jucători!",
        description="Apasă un buton pentru a crea LFG.",
        color=0x2b2d31
    )
    await interaction.response.send_message(embed=embed, view=CautaView())

# ---------------- /CAUTA ----------------
@bot.tree.command(name="cauta", description="Panou căutare jucători")
async def cauta(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔍 Caută jucători!",
        description="Apasă un buton pentru a crea LFG.",
        color=0xff4655
    )
    await interaction.response.send_message(embed=embed, view=CautaView())

# ================= PREMIER =================
@bot.tree.command(name="premier", description="LFG Premier")
async def premier(interaction: discord.Interaction, jucatori: int, rank_range: str, info: str):
    embed = discord.Embed(
        title=f"Premier: Looking for {jucatori} players!",
        color=0xff4655,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="🏆 Rank range", value=rank_range)
    embed.add_field(name="ℹ️ Info", value=info)
    embed.set_footer(text="Valorant România")
    await interaction.response.send_message(embed=embed, view=LFGView(jucatori))

# ---------------- /ANUNT ----------------
@bot.tree.command(name="anunt", description="Anunț oficial")
async def anunt(interaction: discord.Interaction, mesaj: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Doar adminii.", ephemeral=True)

    await interaction.response.send_message(
        embed=discord.Embed(title="📢 ANUNȚ", description=mesaj, color=0xff4655)
    )

# ---------------- RUN ----------------
bot.run(TOKEN)
