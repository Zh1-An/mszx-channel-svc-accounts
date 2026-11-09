# 民生直销银行 · 渠道服务账号清单

民生直销银行渠道接入所用的服务账号登记表，记录账号、令牌、令牌类型、有效期与责任人。
新增或轮换账号需走变更单，由渠道接入组在变更窗口内执行。

## 目录

| 文件 | 说明 |
|---|---|
| `accounts/service-accounts.csv` | 6 个服务账号：系统、环境、账号、令牌、令牌类型、过期日、责任人 |
| `src/credential_loader.py` | 清单加载、令牌前缀校验与按系统分组 |
| `README.md` | 本文档 |

## 渠道标识

渠道名 `民生直销银行`，接入侧系统标识 `mszx`，对应网关实例 `channel-gateway`、
批量清算 `settlement-batch`、风控适配 `risk-adapter`、文件交换 `file-exchange`。

标识出现位置：

- `accounts/service-accounts.csv`：`渠道` 列逐行取值
- `src/credential_loader.py`：`CHANNEL_NAME` 常量、`SYSTEM_PREFIX` 常量
- 本文档：标题与本节

## 使用

```bash
python src/credential_loader.py accounts/service-accounts.csv
```

输出各系统的账号数量与最近到期日；令牌前缀不符或账号命名不合规时打印告警并返回 1。

## 字段说明

| 字段 | 说明 |
|---|---|
| `渠道` | 渠道名称，本清单固定为一个渠道 |
| `系统` | 接入系统标识，小写短横线命名 |
| `环境` | `prod` / `uat` |
| `账号` | 服务账号名，以 `svc_` 开头 |
| `令牌` | 32 位内部令牌，前缀 `int_` |
| `令牌类型` | 固定 `internal`，由内部签发服务统一管理 |
| `过期日` | 令牌到期日，到期前 15 天由轮换任务提醒 |
| `责任人` | 账号责任人，随变更单登记 |

## 已知问题

1. `uat` 环境账号与 `prod` 共用同一套命名规则，环境仅靠后缀区分，易混淆。
2. 令牌轮换任务只更新 `prod`，`uat` 需手工触发。
3. 文件交换账号 `svc_mszx_ftp` 仍使用密码方式登录，尚未切到令牌。

## 维护

渠道接入组（`#channel-access`）。
