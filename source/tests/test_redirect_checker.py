import unittest
from source import redirect_checker
import mock
from argparse import Namespace

def stop_app(*args, **kwargs):
    redirect_checker.app_run = False

def start_app(*args, **kwargs):
    redirect_checker.app_run = True

class RedirectCheckerTestCase(unittest.TestCase):

    def tearDown(self):
        start_app()

    def test_main_loop__network_ok(self):
        #logger = mock.MagicMock()

        config = mock.Mock()
        config.WORKER_POOL_SIZE = 4
        config.SLEEP = 1
        config.CHECK_URL = "http://test.ba"
        config.HTTP_TIMEOUT = 30

        pid = 4242
        active_chilren = [mock.Mock(), mock.Mock()]
        check_network_status = mock.Mock(return_value=True)
        spawn_workers = mock.Mock(side_effect=stop_app)

        #with mock.patch('')
        with mock.patch('os.getpid', mock.Mock(return_value = pid)):
         with mock.patch('source.redirect_checker.check_network_status', check_network_status):
          with mock.patch('source.redirect_checker.active_children', mock.Mock(return_value = active_chilren)):
           with mock.patch('source.redirect_checker.spawn_workers', spawn_workers):
               redirect_checker.main_loop(config=config)

        assert spawn_workers.called


    def test_main_loop__network_fail(self):
        config = mock.Mock()
        config.SLEEP = 1
        config.CHECK_URL = "http://test.ba"
        config.HTTP_TIMEOUT = 30

        pid = 4242
        child = mock.Mock()
        child.terminate = mock.Mock()
        active_chilren = [child, child]
        check_network_status = mock.Mock(return_value=False)
        sleep = mock.Mock(side_effect=stop_app)

        #with mock.patch('')
        with mock.patch('os.getpid', mock.Mock(return_value = pid)):
         with mock.patch('source.redirect_checker.check_network_status', check_network_status):
          with mock.patch('source.redirect_checker.active_children', mock.Mock(return_value = active_chilren)):
           with mock.patch('source.redirect_checker.sleep', sleep):
               redirect_checker.main_loop(config=config)

        assert sleep.called
        assert (child.terminate.call_count == len(active_chilren))


    def test_main__deamon_pidfile(self):

        args = Namespace(config='test', daemon=True, pidfile=True)

        config = mock.Mock()

        main_loop = mock.Mock(side_effect = stop_app)

        with mock.patch('source.redirect_checker.parse_cmd_args', mock.Mock(return_value=args)):
         with mock.patch('source.redirect_checker.daemonize', mock.Mock()) as demonize:
          with mock.patch('source.redirect_checker.create_pidfile', mock.Mock()) as create_pidfile:
           with mock.patch('source.redirect_checker.load_config_from_pyfile', mock.Mock(return_value=config)) as load_config:
            with mock.patch('source.redirect_checker.os.path.realpath', mock.Mock()):
             with mock.patch('source.redirect_checker.os.path.expanduser', mock.Mock()):
              with mock.patch('source.redirect_checker.dictConfig', mock.Mock()):
               with mock.patch('source.redirect_checker.main_loop', main_loop):
                  redirect_checker.main([1,2,3])

        assert demonize.called
        assert create_pidfile.called
        assert load_config.called
        assert main_loop.called


    def test_main__nodeamon_pidfile(self):

        args = Namespace(config='config', daemon=False, pidfile=True)

        config = mock.Mock()

        main_loop = mock.Mock(side_effect = stop_app)

        with mock.patch('source.redirect_checker.parse_cmd_args', mock.Mock(return_value=args)):
         with mock.patch('source.redirect_checker.daemonize', mock.Mock()) as demonize:
          with mock.patch('source.redirect_checker.create_pidfile', mock.Mock()) as create_pidfile:
           with mock.patch('source.redirect_checker.load_config_from_pyfile', mock.Mock(return_value=config)) as load_config:
            with mock.patch('source.redirect_checker.os.path.realpath', mock.Mock()):
             with mock.patch('source.redirect_checker.os.path.expanduser', mock.Mock()):
              with mock.patch('source.redirect_checker.dictConfig', mock.Mock()):
               with mock.patch('source.redirect_checker.main_loop', main_loop):
                  redirect_checker.main([1,2,3])

        assert not demonize.called
        assert create_pidfile.called
        assert load_config.called
        assert main_loop.called


    def test_main__deamon_nopidfile(self):

        args = Namespace(config='config', daemon=True, pidfile=False)

        config = mock.Mock()

        main_loop = mock.Mock(side_effect = stop_app)

        with mock.patch('source.redirect_checker.parse_cmd_args', mock.Mock(return_value=args)):
         with mock.patch('source.redirect_checker.daemonize', mock.Mock()) as demonize:
          with mock.patch('source.redirect_checker.create_pidfile', mock.Mock()) as create_pidfile:
           with mock.patch('source.redirect_checker.load_config_from_pyfile', mock.Mock(return_value=config)) as load_config:
            with mock.patch('source.redirect_checker.os.path.realpath', mock.Mock()):
             with mock.patch('source.redirect_checker.os.path.expanduser', mock.Mock()):
              with mock.patch('source.redirect_checker.dictConfig', mock.Mock()):
               with mock.patch('source.redirect_checker.main_loop', main_loop):
                  redirect_checker.main([1,2,3])

        assert demonize.called
        assert not create_pidfile.called
        assert load_config.called
        assert main_loop.called
