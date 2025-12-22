class StrategyRegistry:
    STRATEGIES = {
        "rsi": "strategies.rsi_strategy.RSIStrategy",
        "dca": "strategies.dca_strategy.DCAStrategy"
    }
    
    @staticmethod
    def load(strategy_name: str):
        """Загрузка стратегии по имени"""
        class_path = StrategyRegistry.STRATEGIES.get(strategy_name)
        if not class_path:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        module_name, class_name = class_path.rsplit(".", 1)
        module = __import__(module_name, fromlist=[class_name])
        return getattr(module, class_name)()
