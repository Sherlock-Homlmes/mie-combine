# default
import discord
from discord import ui

# local
from core.conf.bot.conf import bot

QR_BANK_PATH = "assets/qr-bank-server.jpg"


class HelpView(ui.View):
    @ui.select(
        placeholder=" chọn câu hỏi bạn cần hỗ trợ...",
        min_values=1,
        max_values=1,
        custom_id="help-select",
        options=[
            discord.SelectOption(
                label="Hướng dẫn chọn role trong server",
                value="role_guide",
                emoji="🎭",
            ),
            discord.SelectOption(
                label="Tắt âm thanh voice channel",
                value="voice_sound",
                emoji="🔊",
            ),
            discord.SelectOption(
                label="Cách sử dụng phòng học",
                value="study_room",
                emoji="📚",
            ),
            discord.SelectOption(
                label="Cách gọi bot nhạc",
                value="music_bot",
                emoji="🎵",
            ),
            discord.SelectOption(
                label="Mức phạt khi nói tục",
                value="bad_words",
                emoji="⚠️",
            ),
            discord.SelectOption(
                label="Hỏi đáp về học tập",
                value="study_qa",
                emoji="❓",
            ),
            discord.SelectOption(
                label="Khu vực giải trí",
                value="entertainment",
                emoji="🎮",
            ),
            discord.SelectOption(
                label="Số tài khoản & Thống kê server",
                value="bank_stats",
                emoji="📊",
            ),
            discord.SelectOption(
                label="Có thắc mắc khác",
                value="other_questions",
                emoji="💬",
            ),
        ],
    )
    async def select_callback(self, interaction: discord.Interaction, select):
        selected = select.values[0]

        if selected == "bank_stats":
            await self.send_bank_stats(interaction)
        else:
            embed = await self.get_answer_embed(selected)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    async def send_bank_stats(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📊 Số tài khoản & Thống kê server",
            description=(
                "**💰 Thông tin ủng hộ server:**\n\n"
                "🔗 **Link sao kê:**\n"
                "https://share.timo.vn/VN/transaction/trwbvmnta0de\n\n"
            ),
            color=discord.Colour.gold(),
        )
        embed.set_footer(text="BetterMe - Better everyday")

        file = discord.File(QR_BANK_PATH, filename="qr-bank.jpg")
        embed.set_image(url="attachment://qr-bank.jpg")

        await interaction.response.send_message(embed=embed, file=file, ephemeral=True)

    async def get_answer_embed(self, question: str) -> discord.Embed:
        embed = discord.Embed(color=discord.Colour.gold())

        if question == "role_guide":
            embed.title = "🎭 Hướng dẫn chọn role trong server"
            embed.description = (
                "**Cách thay đổi role:**\n"
                "➤ Vào phần **Kênh & Vai trò** (bên góc trái trên màn hình)\n"
                "➤ Chọn role bạn muốn hiển thị\n\n"
                "**💡 Mẹo:** Bạn cũng có thể ẩn/hiện các kênh theo mong muốn tại đây!"
            )

        elif question == "voice_sound":
            embed.title = "🔊 Tắt âm thanh khi có người vào/ra phòng"
            embed.description = (
                "Âm thanh khi có người vào hoặc ra phòng làm mất tập trung? "
                "Hãy tắt nó theo các bước sau:\n\n"
                "**Bước 1:** Vào phần **Cài đặt người dùng** (User Settings)\n\n"
                "**Bước 2:** Chọn **Voice & Video** → **Sounds**\n\n"
                "**Bước 3:** Tắt 3 mục sau:\n"
                "• Người dùng tham gia (User Join)\n"
                "• Người dùng thoát ra (User Leave)\n"
                "• Người dùng di chuyển (User Move)"
            )

        elif question == "study_room":
            embed.title = "📚 Cách sử dụng phòng học"
            embed.description = (
                "**Phòng học công cộng:**\n"
                "➤ Bạn có thể join bất kỳ room public nào để học\n\n"
                "**Tạo phòng riêng:**\n"
                "➤ Join vào một trong các kênh sau để bot tạo phòng cho bạn:\n"
                "• <#918549426732142653>\n"
                "• <#918549341948497961>\n"
                "• <#918549182107746356>\n"
                "• <#922461169799790642>\n\n"
                "➤ Sau đó bot sẽ đưa bạn đến phòng riêng và hướng dẫn sử dụng"
            )

        elif question == "music_bot":
            embed.title = "🎵 Cách gọi bot nhạc"
            embed.description = (
                "Server sử dụng **Jockie Music** bot để phát nhạc!\n\n"
                "**Các lệnh cơ bản:**\n"
                "• `/play <tên bài hát/link>` - Phát nhạc\n"
                "• `/pause` - Tạm dừng\n"
                "• `/resume` - Tiếp tục phát\n"
                "• `/skip` - Bỏ qua bài hiện tại\n"
                "• `/queue` - Xem danh sách phát\n"
                "• `/clear` - Xóa danh sách phát\n"
                "• `/disconnect` - Ngắt kết nối bot\n\n"
                "**💡 Mẹo:** Bạn có thể dùng link YouTube, Spotify, SoundCloud!"
            )

        elif question == "bad_words":
            embed.title = "⚠️ Mức phạt khi nói tục"
            embed.description = (
                "**Các mức phạt của bot cho hành vi nói tục:**\n\n"
                "• **Lần 1 → 6:** Cảnh báo (Warn)\n"
                "• **Những lần sau:** Timeout tăng dần → Ban\n\n"
                "**📌 Lưu ý:**\n"
                "• Sau **30 ngày**, những vi phạm trước đó sẽ được xóa (trừ khi bị ban)\n"
                "• Bạn sẽ nhận thông báo khi bị timeout/ban\n"
                "• Nếu bot xử lý sai, bạn có thể **report**\n"
                "⚠️ Report sai sẽ bị timeout lâu hơn!"
            )

        elif question == "study_qa":
            embed.title = "❓ Hỏi đáp về học tập"
            embed.description = (
                "Bạn có câu hỏi hoặc thắc mắc về học tập?\n\n"
                "**📍 Đăng câu hỏi tại:** <#1024085192735998022>\n"
                "Để mọi người trong server có thể giúp bạn!\n\n"
                "**🤖 Bot AI hỗ trợ:** <@883974628136087562>\n"
                "Cần gì bạn cứ ping bot, bot sẽ giúp bạn!"
            )

        elif question == "entertainment":
            embed.title = "🎮 Khu vực giải trí"
            embed.description = (
                "Server còn nhiều điều thú vị đang chờ bạn khám phá!\n\n"
                "**💌 Chuyên mục Confession:**\n"
                "➤ <#1281681331004117062>\n"
                "Nơi chia sẻ những câu chuyện thầm kín\n\n"
                "**🎲 Giải trí với trò chơi:**\n"
                "➤ <#924750967277236237>\n"
                "Những trò chơi vui nhộn đang chờ bạn!"
            )

        elif question == "other_questions":
            embed.title = "💬 Có thắc mắc khác"
            embed.description = (
                "Bạn có thắc mắc, đề xuất hoặc muốn báo cáo?\n\n"
                "**📍 Truy cập kênh:** <#1024083239486377995>\n\n"
                "Đội ngũ admin sẽ hỗ trợ bạn sớm nhất có thể! 🙌"
            )

        embed.set_footer(text="BetterMe - Better everyday")
        return embed


@bot.listen()
async def on_ready():
    await bot._fully_ready.wait()
    print("-1.Help ready")


@bot.tree.command(name="help", description="Hướng dẫn sử dụng server")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="❓ Trung tâm hỗ trợ BetterMe",
        description=(
            "Chào mừng bạn đến với BetterMe! 🎉\n\n"
            "Hãy chọn câu hỏi bên dưới để được hỗ trợ.\n"
            "Mọi câu hỏi sẽ được trả lời riêng tư."
        ),
        color=discord.Colour.gold(),
    )
    embed.set_footer(text="BetterMe - Better everyday")

    view = HelpView()
    is_public = interaction.user.id == 880359404036317215
    await interaction.response.send_message(
        embed=embed, view=view, ephemeral=not is_public
    )
