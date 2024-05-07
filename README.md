# MemoFlow
<p align="left">
    <img src='https://img.shields.io/badge/language-python3.9-green'>
    <img src='https://img.shields.io/badge/Docker-Yes-brightgreen'>
    <img src='https://img.shields.io/badge/OpenStack-Architecture-orange'>
</p>
本项目是一个基于 Paste-WebOb-Routes框架 、RESTful API 风格的 python 应用服务，实现向 github 仓库或者坚果云仓库同步 Logseq(或Obsidian) 风格的卡片笔记。

具体来说，卡片笔记内容在后台转换为 Logseq(或Obsidian) 段落格式的字符串，然后同步到云端存储的文档中。由于格式兼容，在配合同步工具（git或坚果云）的情况下，云端文档也很方便在本地笔记应用 Logseq(或Obsidian)中使用。

有一个网页客户端，支持提交、浏览与编辑卡片笔记, 不支持 Markdown 语法, 但是支持 `#Tag`标签, Latex公式, 代码块与超链接。

<div style="display: flex; gap:20px; align-items: flex-end;">
  <div style="flex: 4; items-start:center">
    <img src="https://qyzhizi.cn/img/202405071900184.png" alt="client" width="auto" height="auto" />
    <div align="center">
      <p>桌面网页客户端</p>
    </div>
  </div>
  <div style="flex: 1;">
    <img src="https://qyzhizi.cn/img/202405071900655.png" alt="client" width="auto" height="auto" />
    <div align="center">
      <p>移动端网页客户端</p>
    </div>    
  </div>
</div>

## Usage
本项目实现卡片笔记的在线记录、同步(github 或者 坚果云)。你可以选择在本地使用docker部署，那么这个服务只会在本地运行。或者在云服务器部署，它将成为一个在线服务。

[more information](./docs/usage.md)

## Deployment
[使用docker-compose.yml 部署](./docs/docker_deployment_approach.md)

## Configuration
[MemoFlow Configuration](./docs/memoflow_configuration.md)


## Contributing
Feel free to dive in! Open an issue or submit PRs.
MemoFlow follows PEP 8（Python Enhancement Proposal 8）

## License
This project is licensed under the terms of the [MIT license](./LICENSE)
