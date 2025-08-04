# 聚合网盘资源搜索工具

一个聚合了多个网盘搜索的工具。

## 使用

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行

```bash
streamlit run web_app.py --server.port 11223 --server.address 0.0.0.0
```

然后在浏览器中打开 `http://localhost:11223`


## 配置

编辑 `config.yaml` 文件，可以选择使用哪些源，和过滤那些网盘。


## 效果

![](./images/1.gif)


