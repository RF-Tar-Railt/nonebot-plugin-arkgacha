import asyncio
import json
from dataclasses import asdict
from pathlib import Path
import sys

from arclet.alconna import Alconna, Args, CommandMeta
from arknights_toolkit import need_init
from arknights_toolkit.gacha import ArknightsGacha, GachaUser
from httpx import AsyncClient, ConnectError, TimeoutException
from nonebot import get_driver, on_fullmatch, require
from nonebot.adapters import Event
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_alconna")
require("nonebot_plugin_localstore")
require("nonebot_plugin_saa")
require("nonebot_plugin_apscheduler")

from nonebot_plugin_alconna import AlconnaMatch, Match, on_alconna
from nonebot_plugin_localstore import get_cache_file, get_data_file
from nonebot_plugin_saa import Image, MessageFactory, Text
from nonebot_plugin_apscheduler import scheduler

from .config import Config

driver = get_driver()
global_config = driver.config
config = Config.parse_obj(global_config)

__plugin_meta__ = PluginMetadata(
    name="明日方舟抽卡模拟",
    description="明模拟日方舟抽卡功能，支持模拟十连",
    usage="""\
方舟抽卡 [count = 10]
方舟十连
方舟抽卡帮助
方舟卡池更新    
""",
    homepage="https://github.com/RF-Tar-Railt/nonebot-plugin-arkgacha",
    type="application",
    config=Config,
    extra={
        "author": "RF-Tar-Railt",
        'priority': 3,
        "version": "0.3.0",
    }
)


gacha = ArknightsGacha(config.arkgacha_pool_file or get_data_file("arkgacha", "pool.json"))
user_cache_file = get_cache_file("arkgacha", "user.json")
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
    priority=15,
    block=True
)
simulate_regex = on_fullmatch("方舟十连", priority=16, block=True)
help_regex = on_fullmatch("方舟抽卡帮助", priority=16, block=True)
update_regex = on_fullmatch("方舟卡池更新", priority=16, block=True)

if config.arkgacha_auto_update:
    @scheduler.scheduled_job("cron", hour=16)
    async def update_pool():
        await gacha.update()


@driver.on_startup
async def _():
    if need_init():
        process = await asyncio.create_subprocess_shell(
            f"{Path(sys.executable).parent / 'arkkit'} init -SIMG",
        )
        try:
            await process.communicate()
        except Exception:
            process.kill()
            await process.communicate()


@driver.on_shutdown
async def _():
    with user_cache_file.open("w+", encoding="utf-8") as _f:
        json.dump(userdata, _f, ensure_ascii=False, indent=2)


@help_regex.handle()
async def _():
    await help_regex.finish(
        "可用命令：\n"
        "方舟抽卡 [count = 10]\n"
        "方舟十连\n"
        "方舟抽卡帮助\n"
        "方舟卡池更新\n"
    )


@update_regex.handle()
async def _():
    if new := (await gacha.update()):
        text = (
            f"更新成功，卡池已更新至{new.title}\n"
            "六星角色：\n" +
            "\n".join(f"{i.name} {'【限定】' if i.limit else '【常驻】'}" for i in new.six_chars) +
            "\n五星角色：\n" +
            "\n".join(f"{i.name} {'【限定】' if i.limit else '【常驻】'}" for i in new.five_chars)
        )
        if config.arkgacha_pure_text:
            await update_regex.send(text)
        else:
            try:
                async with AsyncClient() as client:
                    data = await client.get(new.pool)
                await MessageFactory([Text(text), Image(data.content)]).send()
            except (TimeoutException, ConnectError, RuntimeError):
                await update_regex.send(text)
        await update_regex.finish()
    else:
        await update_regex.finish("卡池已是最新")


@gacha_regex.handle()
async def _(event: Event, count: Match[int] = AlconnaMatch("count")):
    session = event.get_user_id()
    if session not in userdata:
        user = GachaUser()
        userdata[session] = asdict(user)
    else:
        user = GachaUser(**userdata[session])
    count = min(max(int(count.result), 1), config.arkgacha_max)
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
    text = (
        f"抽卡次数: {count}\n"
        f"六星角色：\n" +
        "\n".join(f"{i} x{get_six[i]}" for i in get_six) +
        "\n五星角色：\n" +
        "\n".join(f"{i} x{get_five[i]}" for i in get_five) +
        "\n四星角色：\n" +
        f"共{four_count}个四星"
    )
    if config.arkgacha_pure_text:
        await gacha_regex.send(text)
    else:
        img = gacha.create_image(user, data, count, True)
        try:
            await MessageFactory(Image(img)).send()
        except RuntimeError:
            await gacha_regex.send(text)
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
