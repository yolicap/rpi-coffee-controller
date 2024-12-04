import pigpio

class LCDController():

    def __init__(self, ):
        pass

    def init(self):
        pass
    
    def clear(self):
        pass

    def message(self, msg: str):
        pass

    def brewing_message(self):
        self.message("brewing...")

    def keep_warm_message(self):
        self.message("keeping warm")

    def cleaning_message(self):
        self.message("clean me!")

    def ready_message(self):
        self.message("ready to brew")