# MemoFlow
<p align="left">
    <img src='https://img.shields.io/badge/language-python3.9-green'>
    <img src='https://img.shields.io/badge/Docker-Yes-brightgreen'>
    <img src='https://img.shields.io/badge/OpenStack-Architecture-orange'>
</p>
本项目(MemoFlow)是一个基于 Paste-WebOb-Routes 、RESTful API 风格的 python 应用服务，实现向 github 仓库或者坚果云仓库同步 logseq 风格的卡片笔记。另外有一个简陋的、未完善的网页客户端，支持提交、拉取、浏览与编辑（暂不支持）卡片笔记。

具体来说，卡片笔记内容在后台转换为 logseq 段落格式的字符串，然后同步到云端存储的文档中，配合同步工具（git或坚果云）文档可以在本地笔记应用(logseq、obsidian)中展示。

<div style="text-align: center; height: 500px; margin: auto;">
  <img src="https://qyzhizi.cn/img/202307201141763.png" alt="居中显示的图片">
</div>
<div style="text-align: center;">
  <p>网页客户端。</p>
</div>

## Usage
简单来说 MemoFlow 实现卡片笔记的在线记录、同步(github 或者 坚果云)。你可以选择在本地使用docker部署，那么这个服务只会在本地运行，安全可靠。或者在云服务器部署，它将成为一个在线服务，
不过目前没有实现多用户的注册于登录（精力有限）。

[点击查看详细信息](./docs/usage.md)

## Deployment method
[使用docker-compose.yml 部署](./docs/docker_deployment_approach.md)

[linux 环境非docker部署](./docs/linux_deployment_approach.md)

## Remote Sync configuration
[sync_config](./docs/sync_config.md)


## Contributing
Feel free to dive in! pen an issue or submit PRs.
MemoFlow follows PEP 8（Python Enhancement Proposal 8）

## License
This project is licensed under the terms of the [MIT license](./LICENSE)
