import json
from dataclasses import asdict
from nonebot import get_driver, require, on_fullmatch
from nonebot.adapters import Event
from nonebot.plugin import PluginMetadata
from arclet.alconna import Alconna, Args, CommandMeta
from arknights_toolkit.gacha import ArknightsGacha, GachaUser
require("nonebot_plugin_arlconna")
require("nonebot_plugin_localstore")
require("nonebot_plugin_saa")

from nonebot_plugin_alconna import on_alconna, AlcMatches
import nonebot_plugin_localstore as store
from nonebot_plugin_saa import MessageFactory, Image

from .config import Config

driver = get_driver()
global_config = driver.config
config = Config.parse_obj(global_config)

__plugin_meta__ = PluginMetadata(
    name="方舟抽卡",
    description="明日方舟抽卡模拟器",
    usage="方舟抽卡 / 方舟十连",
    extra={
        "author": "RF-Tar-Railt",
        'priority': 16,
    }
)


gacha = ArknightsGacha(config.arkgacha_pool_file or store.get_data_file("arkgacha", "pool.json"))
user_cache_file = store.get_cache_file("arkgacha", "user.json")
if not user_cache_file.exists():
    userdata = {}
else:
    with user_cache_file.open("r", encoding="utf-8") as f:
        userdata = json.load(f)

gacha_regex = on_alconna(
    Alconna(
        "方舟抽卡", Args["count", int, 10],
        meta=CommandMeta(
            description="文字版抽卡，可以转图片发送",
            usage=f"方舟抽卡 [count = 10], count不会超过{config.arkgacha_max}",
            example="方舟抽卡 10",
            compact=True
        )
    ),
    auto_send_output=True,
    comp_config={'timeout': 30},
    priority=16,
    block=True
)
simulate_regex = on_fullmatch(r"方舟十连", priority=16, block=True)
help_regex = on_fullmatch(r"方舟抽卡帮助", priority=16, block=True)
update_regex = on_fullmatch(r"方舟卡池更新", priority=16, block=True)


@driver.on_shutdown
async def _():
    with user_cache_file.open("w+", encoding="utf-8") as _f:
        json.dump(userdata, _f, ensure_ascii=False)


@help_regex.handle()
async def _():
    await help_regex.finish(
        "可用命令：\n"
        "方舟抽卡 [count = 10]\n"
        "方舟十连\n"
        "方舟抽卡帮助\n"
        "方舟抽卡更新\n"
    )


@update_regex.handle()
async def _():
    if new := (await gacha.update()):
        await update_regex.finish(
            f"更新成功，卡池已更新至{new.title}\n"
            "六星角色：\n" +
            "\n".join(f"{i.name} {'【限定】' if i.limit else '【常驻】'}" for i in new.six_chars) +
            "\n五星角色：\n" +
            "\n".join(f"{i.name} {'【限定】' if i.limit else '【常驻】'}" for i in new.five_chars)
        )
    else:
        await update_regex.finish("卡池已是最新")


@gacha_regex.handle()
async def _(event: Event, arp: AlcMatches):
    session = event.get_user_id()
    if session not in userdata:
        user = GachaUser()
        userdata[session] = asdict(user)
    else:
        user = GachaUser(**userdata[session])
    count = min(max(int(arp.count), 1), config.arkgacha_max)

    img = gacha.gacha_with_img(user, count)
    try:
        await MessageFactory(Image(img)).send()
    except RuntimeError:
        data = gacha.gacha(user, count)
        get_six = {}
        get_five = {}
        four_count = 0
        for ten in data:
            for res in ten:
                if res.rarity == 6:
                    get_six[res.name] = get_six.get(res.name, 0) + 1
                elif res.rarity == 5:
                    get_five[res.name] = get_five.get(res.name, 0) + 1
                elif res.rarity == 4:
                    four_count += 1
        await gacha_regex.send(
            f"六星角色：\n" +
            "\n".join(f"{i} x{get_six[i]}" for i in get_six) +
            "\n五星角色：\n" +
            "\n".join(f"{i} x{get_five[i]}" for i in get_five) +
            f"\n四星角色：{four_count}个"
        )
    userdata[session] = asdict(user)
    await gacha_regex.finish()


@simulate_regex.handle()
async def _(event: Event):
    from arknights_toolkit.gacha.simulate import simulate_image

    session = event.get_user_id()
    if session not in userdata:
        user = GachaUser()
        userdata[session] = asdict(user)
    else:
        user = GachaUser(**userdata[session])
    res = gacha.gacha(user, 10)
    img = await simulate_image(res[0])
    try:
        await MessageFactory(Image(img)).send()
    except RuntimeError:
        await simulate_regex.send("图片发送失败")
    userdata[session] = asdict(user)
    await gacha_regex.finish()
