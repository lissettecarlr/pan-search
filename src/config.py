"""
配置管理模块
"""
import yaml
from pathlib import Path
from typing import Optional, Dict, Any


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self._config: Optional[Dict[str, Any]] = None
    
    def load(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件 {self.config_path} 未找到")
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                raw_config = yaml.safe_load(f)
            
            # 确保plugins配置格式正确
            if "plugins" in raw_config:
                plugins_config = raw_config["plugins"]
                if isinstance(plugins_config, dict):
                    # 如果plugins是字典，检查是否有enabled字段
                    if "enabled" not in plugins_config:
                        # 转换旧格式配置（布尔值映射）
                        enabled_plugins = [
                            name for name, enabled in plugins_config.items() 
                            if isinstance(enabled, bool) and enabled
                        ]
                        plugins_config["enabled"] = enabled_plugins
                        # 移除布尔值配置项
                        for key in list(plugins_config.keys()):
                            if isinstance(plugins_config[key], bool):
                                del plugins_config[key]
            
            self._config = raw_config
            return self._config
            
        except Exception as e:
            raise Exception(f"配置文件解析失败: {e}")
    
    def get_config(self) -> Dict[str, Any]:
        """获取配置，如果未加载则先加载"""
        if self._config is None:
            self._config = self.load()
        return self._config
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取嵌套配置值
        
        Args:
            key_path: 配置路径，使用点号分隔，如 'type_filter.enabled_types'
            default: 默认值
            
        Returns:
            配置值
        """
        config = self.get_config()
        keys = key_path.split('.')
        value = config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def reload(self) -> Dict[str, Any]:
        """重新加载配置"""
        self._config = None
        return self.load() 