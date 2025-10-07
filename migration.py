import asyncio

from core.models import CurrencyUnitEnum, Transactions, connect_db
from utils.time_modules import Now

# T3
# 1339947226620755992: 11111
# 905009827871338496: 5555
# 890789640691413062: 5555
# 1222423762188767313: 5555
# 1094987690799284254: 5555

# T4
# 889847139029647360: 5555
# 732693635304521838: 5555

# T5
# 1015242935727566889: 55555
# 456226577798135808: 33333
# 900576060419211324: 11111
# 1269260357579575328: 5555
# 1289254131348803644: 5555
# 868485549495820308: 5555
# 1198753125599805634: 5555

# T6
# 905009827871338496: 55555
# 1015242935727566889: 33333
# 469675482137493505: 11111
# 1342319236017819722: 5555
# 1215672197390012506: 5555
# 1198753125599805634: 5555
# 732693635304521838: 5555
# 703430208006652005: 5555
# 1094987690799284254: 5555
# 1170039518276096073: 5555


# T7
# 905009827871338496: 55555
# 788818255480487936: 33333
# 1269260357579575328: 11111
# 875002064680415232: 5555
# 1094987690799284254: 5555
# 703430208006652005: 5555
# 868496342555721798: 5555
# 1170039518276096073: 5555
# 742759832876220537: 5555
# 741320412503474262: 5555

# T8
# 905009827871338496: 55555
# 1269260357579575328: 33333
# 607422722380660746: 11111
# 868485549495820308: 5555
# 1094987690799284254: 5555
# 912615257116114966: 5555
# 894980362994864150: 5555
# 1138180084814057523: 5555
# 1375756159834783755: 5555
# 889847139029647360: 5555

# T9
# 1269260357579575328: 55555
# 1289254131348803644: 33333
# 607422722380660746: 11111
# 868100786297634827: 5555
# 905009827871338496: 5555
# 894980362994864150: 5555
# 1144697387382739065: 5555
# 833191001266454589: 5555
# 392187919416295426: 5555
# 1094987690799284254: 5555


async def run():
    await connect_db()

    from_user_id = 883974628136087562
    transactions = []

    # T3
    month = 3
    transactions.extend(
        [
            Transactions(
                from_user_id=from_user_id,
                to_user_id=1339947226620755992,
                amount=11111,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=905009827871338496,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=890789640691413062,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=1222423762188767313,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=1094987690799284254,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
        ]
    )

    # T4
    month = 4
    transactions.extend(
        [
            Transactions(
                from_user_id=from_user_id,
                to_user_id=889847139029647360,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=732693635304521838,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
        ]
    )

    # T5
    month = 5
    transactions.extend(
        [
            Transactions(
                from_user_id=from_user_id,
                to_user_id=1015242935727566889,
                amount=55555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=456226577798135808,
                amount=33333,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=900576060419211324,
                amount=11111,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=1269260357579575328,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=1289254131348803644,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=868485549495820308,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=1198753125599805634,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
        ]
    )

    # T6
    month = 6
    transactions.extend(
        [
            Transactions(
                from_user_id=from_user_id,
                to_user_id=905009827871338496,
                amount=55555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=1015242935727566889,
                amount=33333,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=469675482137493505,
                amount=11111,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=1342319236017819722,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=1215672197390012506,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=1198753125599805634,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=732693635304521838,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=703430208006652005,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=1094987690799284254,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=1170039518276096073,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
        ]
    )

    # T7
    month = 7
    transactions.extend(
        [
            Transactions(
                from_user_id=from_user_id,
                to_user_id=905009827871338496,
                amount=55555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=788818255480487936,
                amount=33333,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=1269260357579575328,
                amount=11111,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=875002064680415232,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=1094987690799284254,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=703430208006652005,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=868496342555721798,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=1170039518276096073,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=742759832876220537,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=741320412503474262,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
        ]
    )

    # T8
    month = 8
    transactions.extend(
        [
            Transactions(
                from_user_id=from_user_id,
                to_user_id=905009827871338496,
                amount=55555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=1269260357579575328,
                amount=33333,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=607422722380660746,
                amount=11111,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=868485549495820308,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=1094987690799284254,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=912615257116114966,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=894980362994864150,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=1138180084814057523,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=1375756159834783755,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=889847139029647360,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}/2025",
                created_at=Now().now,
            ),
        ]
    )

    # T9
    month = 9
    transactions.extend(
        [
            Transactions(
                from_user_id=from_user_id,
                to_user_id=1269260357579575328,
                amount=55555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=1289254131348803644,
                amount=33333,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=607422722380660746,
                amount=11111,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=868100786297634827,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=905009827871338496,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=894980362994864150,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=1144697387382739065,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=833191001266454589,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=392187919416295426,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}",
                created_at=Now().now,
            ),
            Transactions(
                from_user_id=from_user_id,
                to_user_id=1094987690799284254,
                amount=5555,
                currency_unit=CurrencyUnitEnum.VND,
                message=f"Betterme trao thưởng leaderboard tháng {month}",
                created_at=Now().now,
            ),
        ]
    )

    print(f"Prepare to insert {len(transactions)} transactions")
    command_ok = input('Type "ok" to start change: ')
    if command_ok == "ok":
        print("Begin live changing")
        await Transactions.insert_many(transactions)
        print("Changing done")


asyncio.run(run())
