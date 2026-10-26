# DDM Basic HTTP Downloader

DDM 的公开基础版：使用 Python 标准库，以单连接下载一个 HTTP/HTTPS 文件。
这是一套可独立运行的简单实现，仅保留基础下载源码。

**完整版 DDM 的最新版、安装包与浏览器助手统一从 [官网](https://ddm.divinexu.cc/) 获取。**
公开仓库只维护此基础下载器，旧完整版 Releases 已移除。

## 使用

需要 Python 3.10 或以上，无需安装第三方依赖。

```sh
python3 download.py 'https://example.com/file.zip' -o file.zip
```

Windows 可将 `python3` 换成 `python`。输出目录需要事先存在。
已有文件不会被覆盖；失败或中断的下载会删除本次未完成的文件。HTTPS 使用系统默认信任验证。

## 范围

- 支持 HTTP/HTTPS、普通重定向和单文件保存。
- 不支持多线程加速、断点续传、BT、视频解析、浏览器接管或授权管理。
- 不包含完整版客户端、官网后台、授权签发实现或任何运行凭据。

## 验证

```sh
python3 -m unittest -v
```

测试启动临时本地 HTTP 服务，验证下载、重定向、错误处理、拒绝覆盖及非 HTTP 协议限制，不访问外部下载站。
