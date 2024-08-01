from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from arclet.alconna import (
    Alconna,
    Args,
    Argv,
    Arparma,
    CommandMeta,
    Option,
    set_default_argv_type,
    store_true,
)
from arclet.alconna.argv import __argv_type__
from arknights_toolkit.update.gacha import generate as generate_gacha
from arknights_toolkit.update.main import fetch
from clilte import BasePlugin, CommandLine, PluginMetadata
from nonebot import logger

from . import gacha, __version__, _config


class Init(BasePlugin):
    def init(self) -> Alconna | str:
        alc = Alconna(
            "init",
            Option(
                "--cover|-C", default=False, action=store_true, help_text="是否覆盖已有的资源文件"
            ),
            meta=CommandMeta("初始化干员数据与图片资源"),
        )
        alc.help_text = "初始化干员数据与图片资源"
        return alc

    def meta(self) -> PluginMetadata:
        return PluginMetadata("init", "0.1.0", "init", ["init"], ["RF-Tar-Railt"], 10)

    def dispatch(self, result: Arparma) -> bool | None:
        if result.find("init"):
            select = 2
            asyncio.run(fetch(select, result.query("init.cover.value", False), proxy=_config.arkgacha_proxy))
            import arknights_toolkit

            base_path = Path(arknights_toolkit.__file__).parent / "resource"
            with (base_path / "ops_initialized").open("w+", encoding="utf-8") as _f:
                _f.write(arknights_toolkit.__version__)
            return False
        return True

    @classmethod
    def supply_options(cls):
        return


class Update(BasePlugin):
    def init(self) -> Alconna | str:
        alc = Alconna(
            "update",
            Args["path/", str, str(gacha.file)],
            meta=CommandMeta("更新抽卡卡池数据; 默认使用插件配置里的或默认的文件路径"),
        )
        alc.help_text = "更新抽卡卡池数据; 默认使用插件配置里的或默认的文件路径"
        return alc

    def meta(self) -> PluginMetadata:
        return PluginMetadata(
            "update", "0.1.0", "update", ["update"], ["RF-Tar-Railt"], 20
        )

    def dispatch(self, result: Arparma) -> bool | None:
        if result.find("path"):
            asyncio.run(
                generate_gacha(Path(result["path"]).absolute(), proxy=_config.arkgacha_proxy)
            )
            return False
        return True

    @classmethod
    def supply_options(cls):
        return


class Clear(BasePlugin):
    def init(self) -> Alconna | str:
        alc = Alconna(
            "clear",
            meta=CommandMeta("清除干员数据与图片资源"),
        )
        alc.help_text = "清除干员数据与图片资源"
        return alc

    def meta(self) -> PluginMetadata:
        return PluginMetadata("clear", "0.1.0", "clear", ["clear"], ["RF-Tar-Railt"], 10)

    def dispatch(self, result: Arparma) -> bool | None:
        if result.find("clear"):
            base_path = Path(__file__).parent.parent.parent / "resource"
            if (base_path / "info.json").exists():
                (base_path / "info.json").unlink()
                logger.info("info.json has been removed")
            for img in (base_path / "operators").iterdir():
                if not img.stem.startswith("profile"):
                    img.unlink(missing_ok=True)
                    logger.info(f"{img.name} has been removed")
            (base_path / "ops_initialized").unlink(missing_ok=True)
            logger.success("resource has been cleared")
            return False
        return True

    @classmethod
    def supply_options(cls) -> list[Option] | None:
        return


arkkit = CommandLine(
    "NB CLI plugin for nonebot-plugin-arkgacha",
    __version__,
    rich=True,
    _name="arkkit",
    load_preset=True,
)
arkkit.add(Init, Update)


def main(*args):
    old_argv_type = __argv_type__.get()
    set_default_argv_type(Argv)
    arkkit.main(*(["arkkit"] + list(args or sys.argv[1:])))
    set_default_argv_type(old_argv_type)
