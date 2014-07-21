import obfsproxy.transports.wfpadtools.message as msg
import unittest
from obfsproxy.transports.wfpadtools import const


class WFPadMessageFactoryTest(unittest.TestCase):

    def setUp(self):
        self.msgFactory = msg.WFPadMessageFactory()

    def tearDown(self):
        pass

    def test_normal_message(self):
        msg = self.msgFactory.createWFPadMessage("payload",
                                                 flags=const.FLAG_DATA)
        pass

    def test_control_message(self):
        # Test control message with no arguments
        ctrlMsgsNoArgs = self.msgFactory.createWFPadControlMessage(
                                                        const.OP_IGNORE)
        self.assertEqual(len(ctrlMsgsNoArgs), 1,
                     "More than one message for control without "
                     "args was created.")
        ctrlMsgNoArgs = ctrlMsgsNoArgs[0]
        self.assertFalse(ctrlMsgNoArgs.args,
                         "The test control message contains args: %s"
                         % ctrlMsgNoArgs.args)

        # Test control message with arguments that fit in payload
        testArgs, expArgs = [1, 2], '[1, 2]'
        ctrlMsgsArgs = self.msgFactory.createWFPadControlMessage(
                                                     const.OP_IGNORE,
                                                     args=testArgs)
        self.assertEqual(len(ctrlMsgsArgs), 1,
                     "More than one message for control without args "
                     "was created.")
        ctrlMsgArgs = ctrlMsgsArgs[0]
        obsArgs = ctrlMsgArgs.args
        self.assertEqual(obsArgs, expArgs,
                         "Observed control message args (%s) and "
                         "expected args (%s) do not match"
                         % (obsArgs, expArgs))

        # Test control message with arguments that do not fit
        testArgs = range(1000)
        expArgs = str(testArgs)
        ctrlMsgsArgs = self.msgFactory.createWFPadControlMessage(
                                                     const.OP_IGNORE,
                                                     args=testArgs)
        self.assertTrue(len(ctrlMsgsArgs) > 1,
                     "No more than one message for control without args "
                     "was created.")


class WFPadMessageExtractorTest(unittest.TestCase):

    def setUp(self):
        self.msgFactory = msg.WFPadMessageFactory()
        self.msgExtractor = msg.WFPadMessageExtractor()

    def tearDown(self):
        pass

    def test_extract_control_message(self):
        testArgs = [range(500), range(500)]
        ctrlMsgsArgs = self.msgFactory.createWFPadControlMessage(
                                                     const.OP_GAP_HISTO,
                                                     args=testArgs)
        strMsg = "".join([str(msg) for msg in ctrlMsgsArgs])
        extractedMsgs = self.msgExtractor.extract(strMsg)
        self.assertEqual(strMsg, "".join([str(msg) for msg in extractedMsgs]),
                         "First extracted messages do not match with"
                         " first original messages.")


class WFPadTransportControlTest(unittest.TestCase):

    def setUp(self):
        self.wfpad = self.WFPadTransport()

    def tearDown(self):
        pass

    def test_receive_control_message(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
