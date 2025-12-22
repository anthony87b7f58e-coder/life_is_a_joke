import os
import yaml

_cfg = None

def load_config(path=None):
    global _cfg
    if _cfg:
        return _cfg
    path = path or os.environ.get('CONFIG_PATH') or os.path.join(os.getcwd(),'config.yaml')
    with open(path,'r',encoding='utf8') as f:
        _cfg = yaml.safe_load(f)
    return _cfg

def get_redis_url():
    cfg = load_config()
    return cfg.get('redis',{}).get('url','redis://localhost:6379/0')
