# libs
import datetime

import aiohttp
import discord
from discord import Interaction, app_commands, ui
from discord.ext import commands

# local
from models import CurrencyUnitEnum, Transactions, Users
from models.users import UserMetadata

# Global cache for bank list
bank_list_cache = {
    "data": None,
    "last_fetched": None,
}


# TODO: update this cache
async def get_vietqr_banks():
    """Fetches the list of banks from VietQR API and caches it for a day."""
    now = datetime.datetime.now()
    if (
        bank_list_cache["data"]
        and bank_list_cache["last_fetched"]
        and (now - bank_list_cache["last_fetched"]).days < 1
    ):
        return bank_list_cache["data"]

    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.vietqr.io/v2/banks") as response:
            if response.status == 200:
                data = await response.json()
                if data.get("code") == "00":
                    # Sort banks alphabetically by shortName
                    sorted_banks = sorted(data["data"], key=lambda x: x["shortName"])
                    bank_list_cache["data"] = sorted_banks
                    bank_list_cache["last_fetched"] = now
                    return sorted_banks
    return None


class UpdateQRModal(ui.Modal):
    def __init__(self, user_id, bank_code):
        super().__init__(title="Cập nhật thông tin QR")
        self.user_id = user_id
        self.bank_code = bank_code

    account_number = ui.TextInput(
        label="Số tài khoản", placeholder="Nhập số tài khoản của bạn"
    )

    async def on_submit(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        account_no = str(self.account_number.value)

        user = await Users.find_one(Users.discord_id == self.user_id)
        if not user.metadata:
            user.metadata = UserMetadata(
                bank_account=account_no, bank_code=self.bank_code
            )
        else:
            user.metadata.bank_account = account_no
            user.metadata.bank_code = self.bank_code

        await user.save()

        # Find bank name from cache
        banks = await get_vietqr_banks()
        bank_name = "Không rõ"
        if banks:
            bank_info = next(
                (bank for bank in banks if bank["bin"] == self.bank_code), None
            )
            if bank_info:
                bank_name = bank_info["shortName"]

        # Send the new QR code
        qr_url = f"https://api.vietqr.io/image/{self.bank_code}-{account_no}-VJgu9fO.jpg?amount=0"
        embed = discord.Embed(
            title="Đã cập nhật thông tin QR thành công! Vui lòng kiểm tra lại thông tin đảm bảo QR này đúng là tài khoản ngân hàng của bạn."
        )
        embed.set_image(url=qr_url)
        embed.add_field(name="Ngân hàng", value=bank_name, inline=True)
        embed.add_field(name="Số tài khoản", value=account_no, inline=True)

        await interaction.followup.send(embed=embed, ephemeral=True)


class BankSelectionView(ui.View):
    def __init__(self, user_id, banks):
        super().__init__(timeout=180)
        self.user_id = user_id

        bank_chunks = [banks[i : i + 25] for i in range(0, len(banks), 25)]

        for i, chunk in enumerate(bank_chunks):
            options = [
                discord.SelectOption(label=bank["shortName"], value=bank["bin"])
                for bank in chunk
            ]
            select_menu = ui.Select(
                placeholder=f"Chọn ngân hàng... (Trang {i + 1})",
                options=options,
                custom_id=f"bank_select_{i}",
            )
            select_menu.callback = self.select_callback
            self.add_item(select_menu)

    async def select_callback(self, interaction: Interaction):
        bank_code = interaction.data["values"][0]
        modal = UpdateQRModal(interaction.user.id, bank_code)
        await interaction.response.send_modal(modal)


class MoneyOptions(ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=180)
        self.user_id = user_id

    @ui.button(
        label="Balance & Transaction", emoji="💰", style=discord.ButtonStyle.primary
    )
    async def get_balance_and_transactions_button(
        self, interaction: Interaction, button: ui.Button
    ):
        await interaction.response.defer(ephemeral=True)
        currency_unit = CurrencyUnitEnum.VND

        # Get balance
        all_income_transaction = await Transactions.find(
            {"to_user_id": self.user_id, "currency_unit": currency_unit}
        ).to_list()
        all_outcome_transaction = await Transactions.find(
            {"from_user_id": self.user_id, "currency_unit": currency_unit}
        ).to_list()
        final_amount = sum(
            [income_transaction.amount for income_transaction in all_income_transaction]
        ) - sum(
            [
                outcome_transaction.amount
                for outcome_transaction in all_outcome_transaction
            ]
        )

        # Get transactions
        page = 1
        embed, has_next_page = await self._get_transaction_data(page)

        balance_content = (
            f"💰 **Số dư hiện tại: {final_amount:,.0f} {currency_unit.value}**"
        )

        if embed is None:
            # Only show balance if no transactions
            await interaction.followup.send(
                content=f"{balance_content}\n\nBạn không có giao dịch nào.",
                ephemeral=True,
            )
        else:
            view = TransactionPagination(self.user_id, page, not has_next_page)
            await interaction.followup.send(
                content=balance_content, embed=embed, view=view, ephemeral=True
            )

    @ui.button(label="QR", emoji="📷", style=discord.ButtonStyle.primary)
    async def get_qr_button(self, interaction: Interaction, button: ui.Button):
        await interaction.response.defer(ephemeral=True)
        user = await Users.find_one(Users.discord_id == self.user_id)

        if not user or not user.metadata or not user.metadata.bank_account:
            await interaction.followup.send(
                content="Bạn chưa cập nhật thông tin ngân hàng. Vui lòng sử dụng nút 'Cập nhật STK'.",
                ephemeral=True,
            )
        else:
            # Find bank name from cache
            banks = await get_vietqr_banks()
            bank_name = "Không rõ"
            if banks:
                bank_info = next(
                    (bank for bank in banks if bank["bin"] == user.metadata.bank_code),
                    None,
                )
                if bank_info:
                    bank_name = bank_info["shortName"]

            qr_url = f"https://api.vietqr.io/image/{user.metadata.bank_code}-{user.metadata.bank_account}-VJgu9fO.jpg?amount=0"
            embed = discord.Embed(title=f"Tài khoản của {user.nick or user.name}")
            embed.set_image(url=qr_url)
            embed.add_field(name="Ngân hàng", value=bank_name, inline=True)
            embed.add_field(
                name="Số tài khoản", value=user.metadata.bank_account, inline=True
            )
            await interaction.followup.send(embed=embed)

    @ui.button(label="Cập nhật STK", emoji="🔄", style=discord.ButtonStyle.secondary)
    async def update_qr_button(self, interaction: Interaction, button: ui.Button):
        await interaction.response.defer(ephemeral=True)
        banks = await get_vietqr_banks()
        if not banks:
            await interaction.followup.send(
                content="Không thể lấy danh sách ngân hàng. Vui lòng thử lại sau.",
                ephemeral=True,
            )
        else:
            view = BankSelectionView(self.user_id, banks)
            await interaction.followup.send(
                content="Vui lòng chọn ngân hàng của bạn:", view=view, ephemeral=True
            )

    async def _get_transaction_data(self, page: int):
        currency_unit = CurrencyUnitEnum.VND
        transactions = (
            await Transactions.find(
                {
                    "$or": [
                        {"to_user_id": self.user_id},
                        {"from_user_id": self.user_id},
                    ],
                    "currency_unit": currency_unit,
                }
            )
            .sort(-Transactions.created_at)
            .skip((page - 1) * 10)
            .limit(11)
            .to_list()
        )

        if not transactions:
            return None, False

        has_next_page = len(transactions) > 10
        display_transactions = transactions[:10]

        embed = discord.Embed(title=f"Lịch sử giao dịch - Trang {page}")
        description = ""
        for trans in display_transactions:
            description += f"**Người chuyển khoản**: <@{trans.from_user_id}> \n"
            description += (
                f"**Số tiền**: {trans.amount:,.0f} {trans.currency_unit.value} \n"
            )
            description += (
                f"**Thời gian:** {trans.created_at.strftime('%H:%M %d/%m/%Y')} \n"
            )
            description += f"**Nội dung:** {trans.message}\n\n"

        embed.description = description
        return embed, has_next_page


class TransactionPagination(ui.View):
    def __init__(self, user_id: int, current_page: int, next_disabled: bool):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.current_page = current_page
        if current_page == 1:
            self.children[0].disabled = True
        self.children[1].disabled = next_disabled

    async def _update_message(self, interaction: Interaction, new_page: int):
        money_options = MoneyOptions(self.user_id)
        embed, has_next = await money_options._get_transaction_data(new_page)
        if embed:
            view = TransactionPagination(self.user_id, new_page, not has_next)
            await interaction.edit_original_response(embed=embed, view=view)
        else:
            await interaction.edit_original_response(
                content="Không có giao dịch nào.", embed=None, view=None
            )

    @ui.button(label="Previous", emoji="⬅️", style=discord.ButtonStyle.grey)
    async def previous_page(self, interaction: Interaction, button: ui.Button):
        await interaction.response.defer()
        await self._update_message(interaction, self.current_page - 1)

    @ui.button(label="Next", emoji="➡️", style=discord.ButtonStyle.grey)
    async def next_page(self, interaction: Interaction, button: ui.Button):
        await interaction.response.defer()
        await self._update_message(interaction, self.current_page + 1)


class MoneyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot._fully_ready.wait()
        self.bot.module_count += 1
        print(f"{self.bot.module_count}. Money module ready")

    class TransactionModal(ui.Modal, title="Tạo giao dịch"):
        amount = ui.TextInput(
            label="Số tiền (VNĐ)",
            placeholder="Nhập số tiền muốn chuyển",
        )

        message = ui.TextInput(
            label="Nội dung chuyển khoản",
            placeholder="Nhập nội dung giao dịch",
            required=False,
            max_length=200,
        )

        def __init__(self, target_user_id: int):
            super().__init__()
            self.target_user_id = target_user_id

        async def on_submit(self, interaction: Interaction):
            await interaction.response.defer(ephemeral=True)

            try:
                amount = float(self.amount.value)
                if amount <= 0:
                    await interaction.followup.send(
                        "❌ Số tiền phải lớn hơn 0!", ephemeral=True
                    )
                    return
            except ValueError:
                await interaction.followup.send(
                    "❌ Số tiền không hợp lệ!", ephemeral=True
                )
                return

            # Show confirmation view
            view = MoneyCog.TransactionConfirmView(
                interaction.user.id,
                self.target_user_id,
                amount,
                self.message.value or "Không có nội dung",
            )

            embed = discord.Embed(title="Xác nhận giao dịch")
            embed.add_field(
                name="Người gửi", value=f"<@{interaction.user.id}>", inline=True
            )
            embed.add_field(
                name="Người nhận", value=f"<@{self.target_user_id}>", inline=True
            )
            embed.add_field(name="Số tiền", value=f"{amount:,.0f} VNĐ", inline=False)
            embed.add_field(
                name="Nội dung",
                value=self.message.value or "Không có nội dung",
                inline=False,
            )

            await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    class UserSelectionView(ui.View):
        def __init__(self, from_user_id: int):
            super().__init__(timeout=180)
            self.from_user_id = from_user_id

            # Use discord.ui.UserSelect for user selection
            user_select = ui.UserSelect(
                placeholder="Chọn người nhận...",
                min_values=1,
                max_values=1,
            )
            user_select.callback = self.select_callback
            self.add_item(user_select)

        async def select_callback(self, interaction: Interaction):
            target_user = interaction.data["values"][0]
            target_user_id = int(target_user)

            # Show modal for amount and message
            modal = MoneyCog.TransactionModal(target_user_id)
            await interaction.response.send_modal(modal)

    class TransactionConfirmView(ui.View):
        def __init__(
            self, from_user_id: int, to_user_id: int, amount: float, message: str
        ):
            super().__init__(timeout=180)
            self.from_user_id = from_user_id
            self.to_user_id = to_user_id
            self.amount = amount
            self.message = message

        @ui.button(label="Xác nhận", style=discord.ButtonStyle.green, emoji="✅")
        async def confirm_button(self, interaction: Interaction, button: ui.Button):
            await interaction.response.defer(ephemeral=True)

            # Create transaction
            transaction = Transactions(
                from_user_id=self.from_user_id,
                to_user_id=self.to_user_id,
                amount=self.amount,
                currency_unit=CurrencyUnitEnum.VND,
                message=self.message,
            )
            await transaction.save()

            embed = discord.Embed(
                title="✅ Giao dịch thành công!", color=discord.Color.green()
            )
            embed.add_field(
                name="Người gửi", value=f"<@{self.from_user_id}>", inline=True
            )
            embed.add_field(
                name="Người nhận", value=f"<@{self.to_user_id}>", inline=True
            )
            embed.add_field(
                name="Số tiền", value=f"{self.amount:,.0f} VNĐ", inline=False
            )
            embed.add_field(name="Nội dung", value=self.message, inline=False)
            embed.add_field(
                name="Thời gian",
                value=datetime.datetime.now().strftime("%H:%M %d/%m/%Y"),
                inline=False,
            )

            await interaction.followup.send(f"<@{self.to_user_id}>", embed=embed)
            self.stop()

        @ui.button(label="Hủy", style=discord.ButtonStyle.red, emoji="❌")
        async def cancel_button(self, interaction: Interaction, button: ui.Button):
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send("❌ Đã hủy giao dịch!", ephemeral=True)
            self.stop()

    @app_commands.command(
        name="transaction", description="Tạo giao dịch chuyển tiền (Chỉ admin)"
    )
    async def transaction_command(self, interaction: Interaction):
        # Check if user is authorized
        if interaction.user.id != 880359404036317215:
            await interaction.response.send_message(
                "❌ Bạn không có quyền sử dụng lệnh này!", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        # Check if in a guild
        if not interaction.guild:
            await interaction.followup.send(
                "❌ Lệnh này chỉ có thể sử dụng trong server!", ephemeral=True
            )
            return

        view = self.UserSelectionView(interaction.user.id)
        await interaction.followup.send(
            "Chọn người nhận tiền:", view=view, ephemeral=True
        )

    @app_commands.command(name="money", description="Kiểm tra số tài khoản hiện tại")
    async def track_money(self, interaction: Interaction):
        view = MoneyOptions(interaction.user.id)
        await interaction.response.send_message(
            "Hãy chọn 1 lựa chọn:", view=view, ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(MoneyCog(bot))
