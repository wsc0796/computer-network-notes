# 计算机网络高质量思维导图

> 用法：不要从头到尾“看图”。每张图都按“题目触发词 -> 标准答案”背。  
> 目标：解决选择题、判断题、简答题答不出来的问题；大题另用计算模板图训练。

---

## 0. 先看哪张

| 时间 | 看法 | 目标 |
|---|---|---|
| 10分钟 | 看 `00 总览` | 知道每层考什么 |
| 25分钟 | 看 `01 选择判断触发词` | 处理客观题陷阱 |
| 35分钟 | 看 `02 简答题模板` | 能写出过程类答案 |
| 45分钟 | 看 `03 网络层计算` | 子网、分片、路由表能算 |
| 35分钟 | 看 `04 TCP专题` | 三次握手、四次挥手、可靠传输能画能解释 |

---

## 1. 00 总览图：按分值优先级记忆

```plantuml
@startmindmap
skinparam BackgroundColor #FFFFFF
skinparam defaultFontName Microsoft YaHei
* 计算机网络期末复习
** [P1] 网络层
*** [大题] IP地址与子网划分
**** 网络地址 = IP & 掩码
**** 广播地址 = 主机位全1
**** 可用主机数 = 2^h - 2
*** [大题] CIDR与最长前缀匹配
**** 前缀越长越精确
**** 多条匹配选最长
*** [大题] IP分片
**** 每片都有IP首部
**** 片偏移单位8字节
**** 最后一片MF=0
*** [选择] 路由协议
**** RIP: 距离向量, 15跳, 16不可达
**** OSPF: 链路状态, Dijkstra
**** BGP: AS之间, 路径向量, 策略
** [P1] 运输层
*** [简答] TCP三次握手
**** SYN -> SYN+ACK -> ACK
**** 防止失效连接请求
*** [简答] TCP四次挥手
**** FIN -> ACK -> FIN -> ACK
**** TIME_WAIT等待2MSL
*** [选择] TCP可靠传输
**** 序号, 确认, 超时重传
**** 滑动窗口, 累积确认
*** [判断] 流量控制 vs 拥塞控制
**** 流量控制看接收方rwnd
**** 拥塞控制看网络cwnd
left side
** [P2] 数据链路层
*** [大题] CRC
**** 生成多项式转二进制
**** 补r个0
**** 模2除法得余数
*** [判断] ARP
**** 请求广播
**** 响应单播
**** 跨网查默认网关MAC
*** [选择] 以太网
**** MAC地址48位
**** 最小帧长64B
**** 交换机按源MAC学习
*** [简答] CSMA/CD
**** 先听后发
**** 边发边听
**** 冲突退避重传
** [P2] 应用层
*** [简答] DNS解析
**** 缓存 -> 本地DNS -> 根 -> TLD -> 权威
*** [选择] HTTP/HTTPS
**** HTTP明文
**** HTTPS = HTTP + TLS
*** [判断] DHCP
**** Discover/Offer/Request/ACK
**** 客户端常用广播
** [P3] 体系结构
*** [简答] 五层模型
**** 应用/运输/网络/链路/物理
*** [选择] PDU
**** 报文/报文段/数据报/帧/比特
@endmindmap
```

---

## 2. 01 选择判断触发词图

背法：遮住箭头右边，只看触发词，强迫自己说答案。

```plantuml
@startmindmap
skinparam BackgroundColor #FFFFFF
skinparam defaultFontName Microsoft YaHei
* 选择判断题触发词
** [判断] ARP
*** 请求怎么发 -> 广播
*** 响应怎么发 -> 单播
*** 路由器是否转发ARP广播 -> 不转发
*** 跨网通信查谁的MAC -> 默认网关MAC
** [判断] IP地址
*** 192.168/172.16/10 -> 私有地址
*** 主机位全0 -> 网络地址
*** 主机位全1 -> 广播地址
*** /24可用主机数 -> 254
*** /30可用主机数 -> 2
** [选择] 路由
*** 多条路由都匹配 -> 最长前缀匹配
*** RIP最大有效跳数 -> 15
*** RIP中16跳 -> 不可达
*** OSPF算法 -> Dijkstra
*** BGP范围 -> AS之间
left side
** [判断] TCP UDP
*** TCP -> 面向连接, 可靠, 字节流
*** UDP -> 无连接, 尽力而为, 报文
*** 端口号长度 -> 16位
*** TCP确认号含义 -> 期望收到的下一个字节序号
** [判断] TCP状态
*** 三次握手第二次 -> SYN+ACK
*** 四次挥手主动方最后 -> TIME_WAIT
*** TIME_WAIT时间 -> 2MSL
*** 为什么四次挥手 -> 全双工, 两方向独立关闭
** [选择] 链路层
*** MAC地址长度 -> 48位
*** 以太网最小帧 -> 64B
*** 交换机学习依据 -> 源MAC
*** CRC功能 -> 检错不是纠错
*** CSMA/CD适用 -> 共享式以太网
** [选择] 应用层
*** DNS常用端口 -> UDP 53
*** HTTP默认端口 -> 80
*** HTTPS默认端口 -> 443
*** DHCP过程 -> DORA
*** FTP控制连接 -> TCP 21
@endmindmap
```

---

## 3. 02 简答题模板图

背法：每个二级节点都按“定义一句话 + 过程/原因 + 易错点”写。

```plantuml
@startmindmap
skinparam BackgroundColor #FFFFFF
skinparam defaultFontName Microsoft YaHei
* 简答题标准答案模板
** [简答] 五层模型与封装
*** 定义
**** 应用层产生报文
**** 运输层加TCP/UDP首部
**** 网络层加IP首部
**** 链路层加帧头帧尾
**** 物理层传比特
*** 浏览器访问网站
**** DNS查IP
**** TCP三次握手
**** HTTP请求响应
**** ARP查下一跳MAC
**** 路由转发
*** 易错
**** PDU名称要对应层次
**** 跨网时MAC逐跳变化, IP端到端不变
** [简答] DNS解析
*** 作用
**** 域名转换为IP地址
*** 过程
**** 浏览器/系统缓存
**** 本地DNS
**** 根DNS
**** 顶级域DNS
**** 权威DNS
*** 易错
**** 根DNS不直接给最终IP
**** 递归和迭代要区分
left side
** [简答] TCP三次握手
*** 过程
**** 客户端发SYN seq=x
**** 服务器回SYN+ACK seq=y ack=x+1
**** 客户端回ACK ack=y+1
*** 为什么三次
**** 确认双方收发能力
**** 防止历史SYN导致误连接
*** 状态
**** 客户端 CLOSED -> SYN_SENT -> ESTABLISHED
**** 服务端 LISTEN -> SYN_RCVD -> ESTABLISHED
** [简答] TCP四次挥手
*** 过程
**** 主动方FIN
**** 被动方ACK
**** 被动方FIN
**** 主动方ACK
*** 为什么四次
**** TCP全双工
**** ACK和FIN常不能立即合并
*** TIME_WAIT
**** 保证最后ACK到达
**** 等旧报文消失
** [简答] 流量控制与拥塞控制
*** 流量控制
**** 防止发送方压垮接收方
**** 接收方通告rwnd
*** 拥塞控制
**** 防止网络过载
**** 慢开始, 拥塞避免, 快重传, 快恢复
*** 对比
**** 对象不同: 接收方 vs 网络
**** 变量不同: rwnd vs cwnd
@endmindmap
```

---

## 4. 03 网络层计算图

背法：按输入类型选择分支。看到题目给什么，就走哪条路线。

```plantuml
@startmindmap
skinparam BackgroundColor #FFFFFF
skinparam defaultFontName Microsoft YaHei
* 网络层大题计算
** [大题] 子网划分
*** 输入1: 给IP/前缀
**** h = 32 - 前缀
**** 地址总数 = 2^h
**** 可用主机 = 2^h - 2
**** 网络地址 = IP & 掩码
**** 广播地址 = 网络地址 + 块大小 - 1
*** 输入2: /24等分n个子网
**** 借位数 = log2(n)
**** 新前缀 = 24 + 借位数
**** 步长 = 256 / n
**** 网络号按0,步长,2步长列
*** 易错
**** 网络地址和广播地址不能给主机
**** 路由器接口也占IP
** [大题] CIDR与聚合
*** 最长前缀匹配
**** 找所有匹配项
**** 选前缀最长的路由
*** 路由聚合
**** 写二进制
**** 找最长公共前缀
**** 公共前缀后置0
**** 写成CIDR
left side
** [大题] IP分片
*** 输入
**** IP总长度
**** IP首部长度
**** MTU
*** 步骤
**** 数据长度 = 总长度 - 首部
**** 每片数据 <= MTU - 首部
**** 非最后片取8字节倍数
**** 片偏移 = 数据起点 / 8
**** 最后一片MF=0
*** 易错
**** 偏移不算IP首部
**** 每个分片都有IP首部
** [大题] RIP更新
*** 输入
**** 原路由表
**** 邻居发来的距离向量
*** 规则
**** 新网络 -> 加入
**** 原下一跳是该邻居 -> 更新
**** 新距离更短 -> 更新
**** 否则不变
*** 固定公式
**** 新距离 = 邻居距离 + 1
**** 大于等于16按不可达
** [大题] CRC
*** 生成多项式 -> 二进制除数
*** 最高次r -> 数据后补r个0
*** 模2除法 -> 余数
*** 发送串 = 原数据 + r位余数
@endmindmap
```

---

## 5. 04 TCP专题图

背法：TCP一定要会“画图 + 解释为什么 + 对比机制”。

```plantuml
@startmindmap
skinparam BackgroundColor #FFFFFF
skinparam defaultFontName Microsoft YaHei
* TCP专题
** [P1][简答] 三次握手
*** 图
**** C -> S: SYN seq=x
**** S -> C: SYN+ACK seq=y ack=x+1
**** C -> S: ACK ack=y+1
*** 状态
**** C: CLOSED -> SYN_SENT -> ESTABLISHED
**** S: LISTEN -> SYN_RCVD -> ESTABLISHED
*** 追问
**** 为什么不是两次
**** 防止失效SYN
**** 确认双方收发能力
** [P1][简答] 四次挥手
*** 图
**** A -> B: FIN
**** B -> A: ACK
**** B -> A: FIN
**** A -> B: ACK
*** 状态
**** A: FIN_WAIT_1 -> FIN_WAIT_2 -> TIME_WAIT -> CLOSED
**** B: CLOSE_WAIT -> LAST_ACK -> CLOSED
*** 追问
**** 为什么通常四次
**** TIME_WAIT为什么2MSL
left side
** [P1][选择] 可靠传输
*** 序号
**** TCP按字节编号
*** 确认
**** ACK表示期望下一个字节
*** 重传
**** 超时重传
**** 快重传: 收到重复ACK
*** 滑动窗口
**** 已确认
**** 已发送未确认
**** 可发送
**** 不可发送
** [P1][判断] 流量控制
*** 目的
**** 不让发送方压垮接收方
*** 变量
**** rwnd接收窗口
*** 典型
**** 接收方通告窗口
** [P1][判断] 拥塞控制
*** 目的
**** 不让网络拥塞
*** 变量
**** cwnd拥塞窗口
*** 算法
**** 慢开始: 指数增长
**** 拥塞避免: 线性增长
**** 快重传
**** 快恢复
*** 发送窗口
**** min(rwnd, cwnd)
@endmindmap
```

---

## 6. 05 链路层与应用层补盲图

```plantuml
@startmindmap
skinparam BackgroundColor #FFFFFF
skinparam defaultFontName Microsoft YaHei
* 链路层与应用层补盲
** [P2] 数据链路层
*** CRC
**** 检错不纠错
**** 模2除法
**** 余数不足补0
*** 透明传输
**** 数据中可能出现定界符
**** 字节填充: ESC
**** 比特填充: 连续5个1后插0
*** CSMA/CD
**** 先听后发
**** 边发边听
**** 冲突退避
**** 争用期2τ
*** 交换机
**** 数据链路层
**** 学习源MAC
**** 根据目的MAC转发
left side
** [P2] 应用层
*** DNS
**** 域名 -> IP
**** UDP 53
**** 缓存降低查询
*** HTTP
**** 请求/响应
**** 无状态
**** 默认80
*** HTTPS
**** HTTP + TLS
**** 加密与身份认证
**** 默认443
*** DHCP
**** 动态分配IP
**** Discover Offer Request ACK
*** NAT
**** 私网地址复用公网IP
**** 修改IP/端口映射
*** ICMP
**** 差错报告与诊断
**** ping使用ICMP回显
@endmindmap
```

---

## 7. 为什么这版比旧图好

| 旧图问题 | 新版处理 |
|---|---|
| 全课程塞进一张图，视觉密度过高 | 拆成 5 张任务图 |
| 节点多但不知道怎么考试 | 每个节点标注 `[选择]`、`[判断]`、`[简答]`、`[大题]` |
| 概念孤立，不能触发答案 | 改为“触发词 -> 标准答案/陷阱” |
| TCP、网络层大题被淹没 | 单独拆出 TCP 图、网络层计算图 |
| 背图时没有顺序 | 给出 10/25/35/45 分钟阅读路径 |

---

## 8. 参考的开源导图思路

- [markdown-viewer/skills - mindmap skill](https://github.com/markdown-viewer/skills/blob/main/mindmap/SKILL.md)：采用 PlantUML mindmap，更适合分左右侧、控制层级。
- [axtonliu/axton-obsidian-visual-skills](https://github.com/axtonliu/axton-obsidian-visual-skills)：适合后续升级成 Obsidian Canvas 或 Excalidraw 版。
- [0x-man/mindmap-skill](https://github.com/0x-man/mindmap-skill)：思路上强调来源、缺口和结构化布局。

