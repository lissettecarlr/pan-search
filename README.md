![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://pan-search-vpddacufbrzd3phwgascjw.streamlit.app/)

# 聚合网盘资源搜索工具

一个聚合了多个网盘搜索源的工具，通过streamlit实现交互，可以自己部署，也可以在`streamlit.io`上直接使用。

## 部署

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动streamlit服务

```bash
streamlit run web_app.py --server.port 11223 --server.address 0.0.0.0
```

然后在浏览器中打开 `http://localhost:11223`

## 配置

编辑 `config.yaml` 文件来自定义应用行为：

```yaml
# 网盘搜索工具配置文件

# 插件配置
plugins:
  enabled:
    # - wanou      
    # - duoduo     
    # - huban       
    # - ouge        
    - jikepan     
    - tgsearch    
    # - hunhepan    
  timeout: 30     # 请求超时时间(秒)
  max_results: 100 # 每个插件最大结果数

# 类型过滤配置
type_filter:
  enabled_types:
    - uc          
    - quark       
    - xunlei      
  # filter_mode: "include" - 只显示enabled_types中的类型
  # filter_mode: "exclude" - 不显示enabled_types中的类型
  # filter_mode: "none" - 不进行过滤，显示所有类型
  filter_mode: "exclude"

```


## 效果

![](./images/1.gif)

## 开发

### 添加新插件

1. 在 `plugins`目录下创建新的插件文件
2. 继承 `PluginBase`类并实现相应方法
3. 在 `config.yaml` 的 `plugins.enabled` 列表中添加插件名称