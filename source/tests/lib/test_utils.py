__author__ = 'Admin'

import unittest
import mock
from source.lib import utils

class UtilsTestCase(unittest.TestCase):
    def test_my_first_test(self):
        self.assertFalse(1 == 2)

    def test_demonize__father(self):
        pid = 4242
        with mock.patch('os.fork', mock.Mock(return_value=pid)) as os_fork:
            with mock.patch('os._exit', mock.Mock()) as os_exit:
                utils.daemonize()

        os_fork.assert_called_once_with()
        os_exit.assert_called_once_with(0)

    def test_demonize__child_child(self):
        pid = 0
        with mock.patch('os.fork', mock.Mock(return_value=pid)) as os_fork:
            with mock.patch('os.setsid', mock.Mock()) as os_setsid:
                with mock.patch('os._exit', mock.Mock()) as os_exit:
                    utils.daemonize()

        os_setsid.assert_called_once_with()
        assert os_fork.called
        assert not os_exit.called

    def test_demonize__child_father(self):
        father_pid = 0
        child_pid = 4242
        with mock.patch('os.fork', mock.Mock(side_effect=[child_pid, father_pid])) as os_fork:
            with mock.patch('os.setsid', mock.Mock()):
                with mock.patch('os._exit', mock.Mock()) as os_exit:
                    utils.daemonize()

        os_exit.assert_called_once_with(0)

    def test_demonize__father_exception(self):
        oserror = OSError("err")
        with mock.patch('os.fork', mock.Mock(side_effect=oserror)):
            self.assertRaises(Exception, utils.daemonize)


    def test_demonize__child_exception(self):
        oserror = OSError("err")
        pid = 0
        with mock.patch('os.fork', mock.Mock(side_effect=[pid,oserror])):
            with mock.patch('os.setsid', mock.Mock()): # as os_setsid:
                """os_setsid.assert_called_once_with() !!!!!! why don't pass?"""
                self.assertRaises(Exception, utils.daemonize)


    def test_create_pidfile(self):
        pid = 4242
        pidfile_path = "random_dir/random_file"
        m_open = mock.mock_open()
        with mock.patch('source.lib.utils.open', m_open, create=True):
            with mock.patch('os.getpid', mock.Mock(return_value = pid)):
                utils.create_pidfile(pidfile_path)

        m_open.assert_called_once_with(pidfile_path, 'w')
        m_open().write.assert_called_once_with(str(pid))


    def test_load_config_from_pyfile(self):
        test_path = "source/tests/lib/testfile_load_config_from_pyfile.py"
        config = utils.load_config_from_pyfile(test_path)
        self.assertEqual(config.NAME_ONE, 4242)
        self.assertEqual(config.NAME_TWO, "MyPluginBaby")
        self.assertEqual(config.NAME_THREE, {
            'one': 'one',
            'two': 4242
        })
        self.assertFalse(hasattr(config, "NameFour"))
        self.assertFalse(hasattr(config, "nameFive"))
        self.assertFalse(hasattr(config, "name_six"))


    def test_check_network_status__ok(self):
        url = "my.url"
        timeout = 5
        with mock.patch('urllib2.urlopen', mock.Mock()):
            self.assertTrue(utils.check_network_status(url, timeout))


    def test_check_network_status__fail_url(self):
        import urllib2
        url = "my.url"
        timeout = 5
        error = urllib2.URLError("error")
        with mock.patch('urllib2.urlopen', mock.Mock(side_effect=error)):
            self.assertFalse(utils.check_network_status(url, timeout))


    def test_parse_cmd_args__alias(self):
        import argparse

        descr = 'description'
        path = '/file/path'
        pid = 4242
        args = '%s -c %s -d -P %d' % (descr, path, pid)
        result = utils.parse_cmd_args(args.split(' ')[1:], descr)
        self.assertEqual(result, argparse.Namespace(config=path, daemon=True, pidfile=str(pid)))

    """def test_spawn_workers(self):
        import multiprocessing
        num = 5
        utils.spawn_workers(num, mock.Mock(), mock.Mock(), mock.Mock())
        with mock.patch('multiprocessing.Process', mock.Mock()) as process:
            self.assertTrue(process.call_count, num)"""


    def test_spawn_workers(self):
        num = 10

        #WHY THIS PATH??????
        #WHY THIS PATH??????
        #WHY THIS PATH??????
        #WHY THIS PATH??????
        #WHY THIS PATH??????
        #WHY THIS PATH??????       \/\/\/\/\/\/\/\/ i want multiprocessing.Process
        with mock.patch("source.lib.utils.Process", mock.Mock()) as process_mock:
            utils.spawn_workers(num, mock.Mock(), mock.Mock(), mock.Mock())
            #self.assertTrue(process_mock.called)
            self.assertEqual(process_mock.call_count, num)




    #def test_get_tube(self):















