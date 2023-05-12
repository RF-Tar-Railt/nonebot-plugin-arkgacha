<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>
</p>

<div align="center">

# NoneBot Plugin Arkgacha

_✨ 明日方舟抽卡模拟器 ✨_

</div>

<p align="center">
  <a href="https://raw.githubusercontent.com/RF-Tar-Railt/nonebot-plugin-arkgacha/master/LICENSE">
    <img src="https://img.shields.io/github/license/RF-Tar-Railt/nonebot-plugin-arkgacha.svg" alt="license">
  </a>
  <a href="https://pypi.python.org/pypi/nonebot-plugin-arkgacha">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-arkgacha.svg" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">
</p>

该插件提供了模拟明日方舟抽卡的功能，包括无头形式的抽卡模拟与模拟十连

通过使用 [`saa`](https://github.com/felinae98/nonebot-plugin-send-anything-anywhere) 插件适配多平台

## 安装

```bash
pip install nonebot-plugin-arkgacha
```

```bash
nb plugin install nonebot-plugin-arkgacha
```

**在使用该插件之前，需要先初始化资源**

```bash
arkkit init
```

## 配置

- ARKGACHA_POOL_FILE: 抽卡池文件路径, 不填则使用 [`localstore`](https://github.com/nonebot/plugin-localstore) 保存抽卡池
- ARKGACHA_MAX: 抽卡最大次数, 默认为 300

## 使用方法

指令如下: 
> 方舟抽卡
> 
> 方舟抽卡 200
> 
> 方舟十连
> 
> 方舟卡池更新


## 效果

> 方舟十连

![res](./test.png)