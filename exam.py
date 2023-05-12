from arknights_toolkit.gacha import ArknightsGacha, GachaUser
import asyncio

ga = ArknightsGacha("temp.json")
user = GachaUser()


async def main():
    from arknights_toolkit.gacha.simulate import simulate_image

    resp = ga.gacha(user, 10)
    data = await simulate_image(resp[0])
    with open("test.png", "wb") as f:
        f.write(data)


asyncio.run(main())
