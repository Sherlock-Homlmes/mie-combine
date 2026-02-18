# libs
import discord
from discord import Interaction, ui

from bot.money import get_vietqr_banks

# local
from core.conf.bot.conf import bot, server_info
from core.models import CurrencyUnitEnum, Transactions, Users


class BalanceCheckView(ui.View):
    def __init__(
        self,
        user_id: int,
        target_user_id: int,
        amount: float,
        has_bank_account: bool = False,
    ):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.target_user_id = target_user_id
        self.amount = amount
        self.has_bank_account = has_bank_account

        # Only add QR button if user has bank account
        if has_bank_account:
            self.add_item(
                ui.Button(
                    label="Generate QR",
                    emoji="📷",
                    style=discord.ButtonStyle.primary,
                    custom_id=f"qr_{target_user_id}",
                )
            )
            # Set the callback for the QR button
            self.children[-1].callback = self.generate_qr_button

    async def generate_qr_button(self, interaction: Interaction):
        # Check if user is admin
        if not any(
            role.id == server_info.role_ids.admin for role in interaction.user.roles
        ):
            await interaction.response.send_message(
                "❌ Bạn không có quyền sử dụng nút này!", ephemeral=True
            )
            return

        await interaction.response.defer()

        user = await Users.find_one(Users.discord_id == self.target_user_id)

        if not user or not user.metadata or not user.metadata.bank_account:
            await interaction.followup.send(
                content=f"❌ Người dùng <@{self.target_user_id}> chưa cập nhật thông tin ngân hàng.",
                ephemeral=True,
            )
            return

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

        qr_url = f"https://api.vietqr.io/image/{user.metadata.bank_code}-{user.metadata.bank_account}-VJgu9fO.jpg?amount={int(self.amount)}&addInfo=Betterme%20chuyển%20tiền"
        embed = discord.Embed(title=f"QR Code thanh toán cho {user.nick or user.name}")
        embed.set_image(url=qr_url)
        embed.add_field(name="Ngân hàng", value=bank_name, inline=True)
        embed.add_field(
            name="Số tài khoản", value=user.metadata.bank_account, inline=True
        )
        embed.add_field(name="Số tiền", value=f"{self.amount:,.0f} VNĐ", inline=False)
        embed.add_field(name="Nội dung", value="Betterme chuyển tiền", inline=False)

        await interaction.followup.send(embed=embed, ephemeral=True)

    @ui.button(
        label="Confirm đã chuyển tiền", emoji="✅", style=discord.ButtonStyle.green
    )
    async def confirm_payment_button(self, interaction: Interaction, button: ui.Button):
        # Check if user is admin
        if not any(
            role.id == server_info.role_ids.admin for role in interaction.user.roles
        ):
            await interaction.response.send_message(
                "❌ Bạn không có quyền sử dụng nút này!", ephemeral=True
            )
            return

        # Show confirmation modal
        modal = ConfirmPaymentModal(self.target_user_id, self.amount)
        await interaction.response.send_modal(modal)


class ConfirmPaymentModal(ui.Modal, title="Xác nhận thanh toán"):
    note = ui.TextInput(
        label="Ghi chú (tùy chọn)",
        placeholder="Nhập ghi chú cho giao dịch này",
        required=False,
        max_length=200,
    )

    def __init__(self, target_user_id: int, amount: float):
        super().__init__()
        self.target_user_id = target_user_id
        self.amount = amount

    async def on_submit(self, interaction: Interaction):
        await interaction.response.defer()

        user = await Users.find_one(Users.discord_id == self.target_user_id)

        if not user or not user.metadata or not user.metadata.bank_account:
            await interaction.followup.send(
                content=f"❌ Người dùng <@{self.target_user_id}> chưa cập nhật thông tin ngân hàng.",
                ephemeral=True,
            )
            return

        bank_account = user.metadata.bank_account
        bank_code = user.metadata.bank_code

        # Find bank name from cache
        banks = await get_vietqr_banks()
        bank_name = bank_code
        if banks:
            bank_info = next(
                (bank for bank in banks if bank["bin"] == bank_code),
                None,
            )
            if bank_info:
                bank_name = bank_info["shortName"]

        # Create transaction
        transaction = Transactions(
            from_user_id=interaction.user.id,
            to_user_id=self.target_user_id,
            amount=self.amount,
            currency_unit=CurrencyUnitEnum.VND,
            message=self.note.value or "Betterme chuyển khoản",
        )
        await transaction.save()

        message = f"Đã thanh toán cho <@{self.target_user_id}> {self.amount:,.0f} VNĐ vào số tài khoản {bank_account} {bank_name}"
        await interaction.followup.send(message)

        # Disable the buttons after confirmation
        if interaction.message:
            # Get the original view and disable buttons
            original_view = BalanceCheckView(
                interaction.user.id,
                self.target_user_id,
                self.amount,
                has_bank_account=True,
            )
            for item in original_view.children:
                item.disabled = True
            await interaction.message.edit(view=original_view)


@bot.tree.command(
    name="balance_check", description="Kiểm tra số dư tất cả người dùng (Chỉ admin)"
)
async def balance_check_command(interaction: Interaction):
    # Check if user is admin
    if not any(
        role.id == server_info.role_ids.admin for role in interaction.user.roles
    ):
        await interaction.response.send_message(
            "❌ Bạn không có quyền sử dụng lệnh này!", ephemeral=True
        )
        return

    await interaction.response.defer()

    # Check if in a guild
    if not interaction.guild:
        await interaction.followup.send(
            "❌ Lệnh này chỉ có thể sử dụng trong server!", ephemeral=True
        )
        return

    # Create a thread
    thread = await interaction.channel.create_thread(
        name=f"Balance Check - {interaction.user.name}",
        type=discord.ChannelType.private_thread,
    )

    await interaction.followup.send(f"Đã tạo thread: {thread.mention}", ephemeral=True)

    # Get all unique user IDs from transactions
    all_transactions = await Transactions.find(
        {"currency_unit": CurrencyUnitEnum.VND}
    ).to_list()

    # Get unique user IDs from both from_user_id and to_user_id
    user_ids = set()
    for trans in all_transactions:
        user_ids.add(trans.from_user_id)
        user_ids.add(trans.to_user_id)

    currency_unit = CurrencyUnitEnum.VND

    for user_id in user_ids:
        # Calculate balance
        all_income_transaction = await Transactions.find(
            {"to_user_id": user_id, "currency_unit": currency_unit}
        ).to_list()
        all_outcome_transaction = await Transactions.find(
            {"from_user_id": user_id, "currency_unit": currency_unit}
        ).to_list()

        total_amount = sum(
            [income_transaction.amount for income_transaction in all_income_transaction]
        ) - sum(
            [
                outcome_transaction.amount
                for outcome_transaction in all_outcome_transaction
            ]
        )

        # Skip users with 0 balance
        if total_amount == 0:
            continue

        # Check if user has bank account
        user = await Users.find_one(Users.discord_id == user_id)
        has_bank_account = (
            user and user.metadata and user.metadata.bank_account is not None
        )

        # Create view with buttons
        view = BalanceCheckView(
            interaction.user.id, user_id, total_amount, has_bank_account
        )

        # Send message for each user
        await thread.send(
            f"<@{user_id}>: {total_amount:,.0f} VNĐ",
            view=view,
        )
