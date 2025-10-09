# Minimal database stub for FAKE_MODE

class DatabaseManager:
    def __init__(self):
        pass
    
    def test_connection(self):
        return True

def get_database():
    return DatabaseManager()
