# BUPTOfferReaper

一个用于统计 offer 信息的 web APP。允许用户匿名分享和交流。用户可以分享 offer 信息，并对 offer 发表评论和投票。

系统无需登录，全匿名，不记录用户信息。

提供基于 RSA 非对称加密算法的加密消息服务。（提交 offer 信息的人可以指定或由系统自动生成一个密钥对，公钥会在网页上公开）

## 安装依赖

```
pip install requirements.txt
```

## 运行

```
python main.py
```



TODO：

- Offer 比较和投票
- 自动发送加密消息（私信）
- 修改和删除 offer 信息
- 搜索和筛选



欢迎 PR！



![](demo.png)