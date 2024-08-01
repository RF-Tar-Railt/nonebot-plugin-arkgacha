import json
from dataclasses import asdict
from pathlib import Path

from arclet.alconna import Alconna, Args, CommandMeta
import arknights_toolkit as arkkit
from arknights_toolkit.update.main import fetch
from arknights_toolkit.gacha import ArknightsGacha, GachaUser
from nonebot.exception import ActionFailed, NetworkError
from nonebot import get_driver, get_plugin_config, on_fullmatch, require, logger
from nonebot.adapters import Event
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_alconna")
require("nonebot_plugin_localstore")
require("nonebot_plugin_apscheduler")

from nonebot_plugin_alconna import Match, UniMessage, SerializeFailed, on_alconna, MsgTarget, SupportScope
from nonebot_plugin_localstore import get_cache_file, get_data_file
from nonebot_plugin_apscheduler import scheduler

from .config import Config

driver = get_driver()
_config = get_plugin_config(Config)
__version__ = "0.8.0"
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
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    extra={
        "author": "RF-Tar-Railt",
        'priority': 3,
        "version": __version__,
    }
)


gacha = ArknightsGacha(
    _config.arkgacha_pool_file or get_data_file("arkgacha", "pool.json"),
    proxy=_config.arkgacha_proxy
)
user_cache_file = get_cache_file("arkgacha", "user.json")
if not user_cache_file.exists():
    userdata = {}
else:
    with user_cache_file.open("r", encoding="utf-8") as f:
        userdata = json.load(f)

gacha_cmd = on_alconna(
    Alconna(
        "方舟抽卡", Args["count", int, 10],
        meta=CommandMeta(
            description="文字版抽卡，可以转图片发送",
            usage=f"方舟抽卡 [count = 10], count不会超过{_config.arkgacha_max}",
            example="方舟抽卡 10",
            compact=True
        )
    ),
    auto_send_output=True,
    skip_for_unmatch=False,
    priority=15,
    block=True
)
simulate_regex = on_fullmatch("方舟十连", priority=16, block=True)
help_regex = on_fullmatch("方舟抽卡帮助", priority=10, block=True)
update_regex = on_fullmatch("方舟卡池更新", priority=16, block=True)

if _config.arkgacha_auto_update:
    @scheduler.scheduled_job("cron", hour=16)
    async def update_pool():
        await gacha.update()


@driver.on_startup
async def _():
    if arkkit.need_init():
        await fetch(2, True, proxy=_config.arkgacha_proxy)
        base_path = Path(arkkit.__file__).parent / "resource"
        with (base_path / "ops_initialized").open("w+", encoding="utf-8") as _f:
            _f.write(arkkit.__version__)
        logger.success("初始化明日方舟抽卡模块完成")


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
        if _config.arkgacha_pure_text:
            await update_regex.send(text)
        else:
            try:
                await UniMessage.image(url=new.pool).send()
            except (ActionFailed, NetworkError, SerializeFailed):
                await update_regex.send(text)
        await update_regex.finish()
    else:
        await update_regex.finish("卡池已是最新")


@gacha_cmd.handle()
async def _(event: Event, count: Match[int], target: MsgTarget):
    session = event.get_user_id()
    if session not in userdata:
        user = GachaUser()
        userdata[session] = asdict(user)
    else:
        user = GachaUser(**userdata[session])
    _count = min(max(int(count.result), 1), _config.arkgacha_max)
    data = gacha.gacha(user, _count)
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
    reply_to = _config.arkgacha_reply_sender
    if target.scope is SupportScope.qq_api and not target.parent_id:
        reply_to = False
    if _config.arkgacha_pure_text:
        await UniMessage.text(text).send(reply_to=reply_to)
    else:
        img = gacha.create_image(user, data, _count, True)
        try:
            await UniMessage.image(raw=img, mimetype="image/jpeg").send(reply_to=reply_to)
        except (ActionFailed, NetworkError, SerializeFailed):
            await UniMessage.text(text).send(reply_to=reply_to)
    userdata[session] = asdict(user)
    await gacha_cmd.finish()


@simulate_regex.handle()
async def _(event: Event, target: MsgTarget):
    from arknights_toolkit.gacha.simulate import simulate_image

    session = event.get_user_id()
    if session not in userdata:
        user = GachaUser()
        userdata[session] = asdict(user)
    else:
        user = GachaUser(**userdata[session])
    res = gacha.gacha(user, 10)
    img = await simulate_image(res[0], proxy=_config.arkgacha_proxy)
    reply_to = _config.arkgacha_reply_sender
    if target.scope is SupportScope.qq_api and not target.parent_id:
        reply_to = False
    try:
        await UniMessage.image(raw=img, mimetype="image/jpeg").send(reply_to=reply_to)
    except (ActionFailed, NetworkError, SerializeFailed):
        await UniMessage.text("图片发送失败").send(reply_to=reply_to)
    userdata[session] = asdict(user)
    await gacha_cmd.finish()
