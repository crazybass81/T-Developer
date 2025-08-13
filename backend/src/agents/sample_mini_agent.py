"""
Ultra-lightweight sample agent for Evolution System
Size: < 6.5KB
Speed: < 3μs instantiation
"""


class MiniAgent:
    """Minimal agent implementation"""

    def __init__(self):
        self.v = "1.0"
        self.d = {}

    def process(self, i):
        """Process input"""
        return {"r": str(i), "v": self.v}

    def analyze(self, d):
        """Analyze data"""
        return len(d) if isinstance(d, (list, dict, str)) else 0

    def transform(self, x):
        """Transform input"""
        return x[::-1] if isinstance(x, str) else x
