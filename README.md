# MemoCard
<p align="left">
    <img src='https://img.shields.io/badge/language-python3.9-green'>
    <img src='https://img.shields.io/badge/Docker-Yes-brightgreen'>
    <img src='https://img.shields.io/badge/OpenStack-Architecture-orange'>
</p>
logseq与obsidian是很好的本地笔记，通过强大双链与标签搜索功能可以非常方便地记录、管理卡片笔记，配合远程仓库(github或者坚果云)可以实现笔记的线上同步。但是如果我想让仓库中某一个文档成为在线页面呢？相比logseq，在浏览器页面中可以更便捷地浏览、记录卡片笔记，并且该页面会被立即同步到远程仓库中，而本地依然可以利用logseq或obsidian的链接与标签搜索功能来纳管该页面。因此MemoCard作为一个连接工具打算提供这种卡片笔记在线浏览、编辑与同步的服务。

## Usage
简单来说MemoCard是一个卡片笔记服务, 主要目的是向远程文件(github 或者坚果云)发送卡片笔记，实现一个轻量化在线卡片笔记的编辑与同步服务。MemoCard页面能够在浏览器显示，并且同步到logseq、obsidian的远程仓库(github 或者坚果云)的文件中。你可以选择在本地使用docker部署，那么这个服务只会在本地运行，安全可靠。或者在云服务器部署，它将成为一个在线服务。

[点击查看详细信息](./docs/usage.md)

## Deployment method
[使用docker-compose.yml 部署](./docs/docker_deployment_approach.md)

[linux 环境非docker部署](./docs/linux_deployment_approach.md)

## Remote Sync configuration
[sync_config](./docs/sync_config.md)


## Contributing
Feel free to dive in! pen an issue or submit PRs.
MemoCard follows PEP 8（Python Enhancement Proposal 8）

## License
This project is licensed under the terms of the [MIT license](./LICENSE)
