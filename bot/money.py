# libs
from discord import Interaction

# local
from core.conf.bot.conf import bot
from core.models import CurrencyUnitEnum, Transactions

# from utils.time_modules import Now


@bot.listen()
async def on_ready():
    global all_created_vc_id, guild

    print("999.Money module ready")


# track, set qr, transaction
@bot.tree.command(name="money", description="Kiểm tra số tài khoản hiện tại")
async def track_money(interaction: Interaction):
    user_id = interaction.user.id
    # transactions_time = Now().now
    currency_unit = CurrencyUnitEnum.VND
    # await Transactions(
    #     from_user_id=883974628136087562,
    #     to_user_id=user_id,
    #     amount=55555,
    #     currency_unit=CurrencyUnitEnum.VND,
    #     created_at=transactions_time,
    # ).insert()

    all_income_transaction = await Transactions.find(
        {"to_user_id": user_id, "currency_unit": currency_unit}
    ).to_list()
    all_outcome_transaction = await Transactions.find(
        {"from_user_id": user_id, "currency_unit": currency_unit}
    ).to_list()
    final_amount = sum(
        [income_transaction.amount for income_transaction in all_income_transaction]
    ) - sum([outcome_transaction.amount for outcome_transaction in all_outcome_transaction])
    await interaction.response.send_message(
        f"""
Tài khoản:
{final_amount} {currency_unit.value}
    """
    )
