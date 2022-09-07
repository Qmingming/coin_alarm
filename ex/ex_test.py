
class Test:
    name = "btc"
    mark_price = 1000
    price = 1100
    emoticon = "smily"

    def __init__(self):
        pass

    def run(self):
        print("%s [%s] %s -> %s (%.2f%%})"
                      % (self.emoticon, self.name, self.mark_price, self.price, (self.price/self.mark_price-1)*100))

test1 = Test()
test1.run()