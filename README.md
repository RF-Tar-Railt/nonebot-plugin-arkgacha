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

通过使用 [`plugin-alconna`](https://github.com/nonebot/plugin-alconna) 插件适配多平台

## 安装

```bash
$ pip install nonebot-plugin-arkgacha
```

```bash
$ nb plugin install nonebot-plugin-arkgacha
```

**在使用该插件之前，需要先初始化资源**

命令行输入：
```bash
nb arkgacha init
```

或

```bash
arkkit init -SIMG
```

## 配置

- ARKGACHA_PROXY: 代理配置，默认为空
- ARKGACHA_POOL_FILE: 抽卡池文件路径, 不填则使用 [`localstore`](https://github.com/nonebot/plugin-localstore) 保存抽卡池
- ARKGACHA_MAX: 抽卡最大次数, 默认为 300
- ARKGACHA_PURE_TEXT: 是否使用纯文本, 默认为 False (十连模拟必须使用图片)
- ARKGACHA_AUTO_UPDATE: 是否自动更新，默认为 True

## 注意事项
1. `方舟抽卡` 不需要图片资源, 可在不经过 `nb arkgacha init` 或 `arkkit init` 的情况下使用
2. `方舟十连` 需要图片资源, 需要先在命令行中执行 `nb arkgacha init` 或 `arkkit init -SIMG` 初始化资源，否则会出现错误
3. 若配置，每天 16 点将自动更新卡池资源
4. 如果获取资源时出现网络错误，请检查代理设置，或尝试访问 PRTS

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
