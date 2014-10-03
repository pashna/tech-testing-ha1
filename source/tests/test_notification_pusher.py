import unittest
import mock
import source.notification_pusher
from source.notification_pusher import create_pidfile


class NotificationPusherTestCase(unittest.TestCase):
    def test_create_pidfile_example(self):
        pid = 42
        m_open = mock.mock_open()
        with mock.patch('source.notification_pusher.open', m_open, create=True):
            with mock.patch('os.getpid', mock.Mock(return_value=pid)) as os_git:
                create_pidfile('/file/path')

        m_open.assert_called_once_with('/file/path', 'w')
        m_open().write.assert_called_once_with(str(pid))

    def test_my_first_test(self):
        self.assertFalse(1 == 2)

    def test_fuck(self):
        foo = 10
        with mock.patch('source.notification_pusher.fuckyou') as fuck:
            fuck.return_value = 10
            print("FUNC = ", source.notification_pusher.fuckmyself())
            self.assertTrue(source.notification_pusher.fuckmyself() == 10)





