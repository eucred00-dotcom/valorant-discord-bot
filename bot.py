import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
from datetime import datetime

# ---------------- ENV ----------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
SQUAD_CATEGORY_ID = 1454795148373524726

# ---------------- INTENTS ----------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

last_cauta_message = {}

# ---------------- /PING ----------------
@bot.tree.command(name="ping", description="Test bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")


# ================= CAUTA VIEW =================
class CautaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def vc_check(self, interaction: discord.Interaction) -> bool:
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message(
                "❌ Trebuie să fii într-un **voice channel** ca să cauți jucători!",
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Ranked", style=discord.ButtonStyle.primary, custom_id="cauta_ranked")
    async def ranked(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.vc_check(interaction):
            return
        await interaction.response.send_modal(LFGModal("Ranked"))

    @discord.ui.button(label="Unranked", style=discord.ButtonStyle.secondary, custom_id="cauta_unranked")
    async def unranked(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.vc_check(interaction):
            return
        await interaction.response.send_modal(LFGModal("Unranked"))

    @discord.ui.button(label="Premier", style=discord.ButtonStyle.success, custom_id="cauta_premier")
    async def premier(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.vc_check(interaction):
            return
        await interaction.response.send_modal(LFGModal("Premier"))

# ---------------- /REGULI ----------------
@bot.command(name="reguli")
async def reguli_prefix(ctx: commands.Context):

    # 1️⃣ POZA SUS
    file = discord.File("valorant_banner.png", filename="valorant_banner.png")
    await ctx.send(file=file)

    # 2️⃣ REGULI JOS
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

    embed.set_footer(text="Sancțiuni temporare sau permanente")

    await ctx.send(embed=embed)

# ================= LFG JOIN =================
class LFGJoinView(discord.ui.View):
    def __init__(self, owner: discord.Member):
        super().__init__(timeout=None)
        self.owner = owner

    @discord.ui.button(label="Join", style=discord.ButtonStyle.success, emoji="🎮")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.defer(ephemeral=True)

        if not self.owner.voice or not self.owner.voice.channel:
            return

        try:
            await interaction.user.move_to(self.owner.voice.channel)
        except:
            pass

# ================= LFG MODAL =================
class LFGModal(discord.ui.Modal):
    def __init__(self, mod: str):
        super().__init__(title=f"LFG {mod}")
        self.mod = mod

        self.jucatori = discord.ui.TextInput(label="Câți jucători cauți?")
        self.rank_range = discord.ui.TextInput(label="Rank range")

        self.add_item(self.jucatori)
        self.add_item(self.rank_range)

    async def on_submit(self, interaction: discord.Interaction):
        # safety: trebuie să fie în VC
        if not interaction.user.voice or not interaction.user.voice.channel:
            return await interaction.response.send_message(
                "❌ Trebuie să fii într-un **voice channel**!",
                ephemeral=True
            )

        voice = interaction.user.voice.channel
        channel = interaction.channel

        # 1️⃣ LFG embed
        embed = discord.Embed(
            title=f"🔊 Caut {self.jucatori.value} jucători!",
            color=0xff4655,
            timestamp=datetime.utcnow()
        )

        embed.add_field(name="Rank-uri", value=self.rank_range.value, inline=True)
        embed.add_field(name="Mod", value=self.mod, inline=True)
        embed.add_field(name="Canal", value=voice.mention, inline=True)

        embed.set_footer(
            text=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(
            embed=embed,
            view=LFGJoinView(interaction.user)
        )

        # 2️⃣ ștergem VECHIUL "Caută jucători"
        if channel.id in last_cauta_message:
            try:
                await last_cauta_message[channel.id].delete()
            except:
                pass

        # 3️⃣ retrimitem UNICUL mesaj "Caută jucători" ULTIMUL
        cauta_embed = discord.Embed(
            title="🔍 Caută jucători!",
            description="Apasă un buton pentru a crea LFG.",
            color=0xff4655
        )

        msg = await channel.send(embed=cauta_embed, view=CautaView())
        last_cauta_message[channel.id] = msg

# ---------------- LOCK CAUTA ----------------
@bot.command(name="lockcauta")
@commands.has_permissions(administrator=True)
async def lock_cauta(ctx):
    channel = ctx.channel

    # blocăm userii normali
    overwrite = channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    overwrite.add_reactions = False

    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

    # permitem botului
    bot_overwrite = channel.overwrites_for(ctx.guild.me)
    bot_overwrite.send_messages = True
    bot_overwrite.embed_links = True

    await channel.set_permissions(ctx.guild.me, overwrite=bot_overwrite)

    await ctx.send("🔒 Canal LOCKED. Doar butoanele funcționează.")


# ---------------- /ANUNT ----------------
@bot.tree.command(name="anunt", description="Anunț oficial")
async def anunt(interaction: discord.Interaction, mesaj: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Doar adminii.", ephemeral=True)

    await interaction.response.send_message(
        embed=discord.Embed(title="📢 ANUNȚ", description=mesaj, color=0xff4655)
    )

@bot.tree.command(name="cauta", description="Caută jucători Valorant")
async def cauta(interaction: discord.Interaction):
    channel = interaction.channel

    # ștergem mesajul vechi dacă există
    if channel.id in last_cauta_message:
        try:
            await last_cauta_message[channel.id].delete()
        except:
            pass

    embed = discord.Embed(
        title="🔍 Caută jucători!",
        description="Apasă un buton pentru a crea LFG.",
        color=0xff4655
    )

    await interaction.response.send_message(embed=embed, view=CautaView())
    last_cauta_message[channel.id] = await interaction.original_response()


# ---------------- READY ----------------
@bot.event
async def on_ready():
    await bot.tree.sync()
    bot.add_view(CautaView())
    print(f"🔥 Bot online: {bot.user}")

# ---------------- RUN ----------------
bot.run(TOKEN)
