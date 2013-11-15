from BaseBridgeTest import BaseBridgeTest


class TestSequenceFunctions(BaseBridgeTest):
    def test_PutGet(self):
        print "put command"
        message = 'Da\xFE5'
        self.send(message)

        print "get command"
        message = 'da'
        self.send(message)
        print self.ser.read()


if __name__ == '__main__':
    unittest.main()
