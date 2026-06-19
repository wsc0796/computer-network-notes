# 百度网盘资料接入流程

> 目标：用 Windows 版 Codex App + 官方 Chrome 扩展，安全查看百度网盘资料，选择性下载计算机网络期末复习相关文件，再在本地提取整理成复习笔记。

---

## 0. 当前限制

本线程没有可调用的 `@Chrome` 浏览器控制工具，所以这里不直接操作百度网盘页面。

你需要在 Windows 版 Codex App 中启用 Chrome 插件后，新开一个对话，把 `prompts/` 里的阶段 Prompt 复制进去执行。

---

## 1. 推荐目录

当前已在本项目下建立：

```text
08_网盘资料接入/
├─ downloads/     # Chrome 下载到这里
├─ extracted/     # 每个源文件提取出的 Markdown
├─ notes/         # 最终复习笔记
├─ logs/          # 清单、计划、冲突记录
└─ prompts/       # 可复制给 Codex 的阶段任务
```

建议把 Chrome 下载位置设置为：

```text
C:\Users\50469\Desktop\Shirakoko_Notes\计算机网络（自顶向下方法）课程笔记_输出\08_网盘资料接入\downloads
```

---

## 2. 执行顺序

1. 你亲自创建独立 Chrome 用户配置，例如 `Codex-临时浏览器`。
2. 在该配置中登录百度网盘，只装 Codex Chrome extension。
3. 新开 Codex 对话，使用 `@Chrome`。
4. 先执行：[01_Chrome查看网盘清单.md](prompts/01_Chrome查看网盘清单.md)。
5. 看清单后，再执行：[02_Chrome选择性下载.md](prompts/02_Chrome选择性下载.md)。
6. 下载结束后，在本地项目执行：[03_本地提取整理.md](prompts/03_本地提取整理.md)。
7. 如果主要是视频，再执行：[04_视频字幕处理.md](prompts/04_视频字幕处理.md)。

---

## 3. 安全边界

- 登录、验证码、短信验证必须由你本人完成。
- 只允许访问 `pan.baidu.com`。
- 不安装百度网盘客户端。
- 不运行 `exe`、`bat`、`cmd`、`msi`、`ps1` 等文件。
- 不删除、移动或修改网盘中的任何内容。
- 先列清单，再选择性下载，不全量下载。
- 单个文件超过 500MB 暂停询问。
- 总下载量预计超过 2GB 暂停询问。

---

## 4. 官方文档依据

- OpenAI Codex Chrome extension 文档说明：Chrome 扩展适合需要已登录浏览器状态的网站任务，并且 Codex 会按网站 host 请求授权。
- 该文档也提醒：网页内容应视为不可信上下文；Chrome 扩展权限可能包括网页读写、浏览历史、下载管理、书签和调试权限。
- Windows 文档说明：Codex App 支持 Windows，并强调本地文件访问和沙箱边界的重要性。

参考：

- <https://developers.openai.com/codex/app/chrome-extension>
- <https://developers.openai.com/codex/windows>

