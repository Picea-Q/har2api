# har2api

把一份浏览器抓包（HAR）读成一张**能直接粘进文档的接口清单**。

## 为什么做这个

手动从浏览器开发者工具里一条条抄接口，是最费时间也最容易抄错的一步：

- 同一个接口被调了几十次，你还得数
- 哪些接口要鉴权、哪些不要，要一条条点开看请求头
- 请求体里到底传了哪些字段，全靠眼睛找
- 抄完还要排版成表格发给同事

`har2api` 干的就是这件事：**给它一份 HAR，它给你一张表。**

## 快速开始

```bash
python har2api.py examples/sample.har
```

存成文件：

```bash
python har2api.py examples/sample.har -o interfaces.md
```

不装任何第三方包，Python 3.8+ 就能跑。

## 怎么拿到 HAR

1. Chrome / Edge 按 `F12` 打开开发者工具
2. 切到 `网络`（Network）标签
3. 操作你要分析的那个网站 / App 的网页版
4. 右上角找一个向下的箭头（导出 HAR），保存成 `.har` 文件

## 输出长这样

| # | 方法 | 域名 | 路径 | 次数 | 状态码 | 平均耗时 | 鉴权头 | 请求体字段 |
|---|---|---|---|---|---|---|---|---|
| 1 | POST | https://api.example.com | /v1/login | 1 | 200 | 120 ms | - | username, password |
| 2 | GET | https://api.example.com | /v1/profile | 3 | 200, 304 | 56 ms | Authorization | - |
| 3 | GET | https://cdn.example.com | /a.js | 1 | 200 | 12 ms | - | - |

## 当前版本（v0.1.0）能做什么

- 按 `方法 + 域名 + 路径` 聚合，自动去掉重复
- 统计每个接口被调用的次数
- 汇总状态码（`304` 这类不算错误，会如实列出）
- 计算平均耗时（跳过耗时缺失的记录）
- 标出用了哪些鉴权头（`Authorization` / `Cookie` / `token` 等）
- 从 JSON 请求体里摘出字段名

## Roadmap

- [ ] v0.2 支持查询参数（`?a=1&b=2` 里的字段也列出来）
- [ ] v0.2 支持拖进多个 HAR 一起合并
- [ ] v0.3 导出成 OpenAPI 风格的 YAML
- [ ] v0.3 标出「疑似加密参数」（名字里带 `sign` / `nonce` / `ts` 且值看起来像哈希）

## License

MIT
