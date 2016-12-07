from BaseBridgeTest import *

class TestSequenceFunctions(BaseBridgeTest):
    def test_PutGet(self):
        print "put command"
        message = 'Dk\xFEb'
        self.datas.transfer(message)

        print "get command"
        message = 'dk'
        self.datas.transfer(message)

if __name__ == '__main__':
    unittest.main()
