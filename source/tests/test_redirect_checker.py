import unittest
from source import redirect_checker
import mock

def check_stop(*arg):
    redirect_checker.app_run = False
def stop_app(*arg):
    redirect_checker.app_run = False

class RedirectCheckerTestCase(unittest.TestCase):

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
        spawn_workers = mock.Mock(side_effect=check_stop)

        #with mock.patch('')
        with mock.patch('os.getpid', mock.Mock(return_value = pid)):
         with mock.patch('source.redirect_checker.check_network_status', check_network_status):
          with mock.patch('source.redirect_checker.active_children', mock.Mock(return_value = active_chilren)):
           with mock.patch('source.redirect_checker.spawn_workers', spawn_workers):
               redirect_checker.main_loop(config=config)

        assert spawn_workers.called
        #assert self.config.WORKER_POOL_SIZE.called
        assert 1==1

    #def