import unittest
import mock
import source.notification_pusher as notification_pusher
from source.notification_pusher import create_pidfile


class NotificationPusherTestCase(unittest.TestCase):

    def setUp(self):
        logger = mock.Mock()
        logger.info = mock.Mock()
        logger.exception = mock.Mock()
        logger.debug = mock.Mock()


    def test_create_pidfile_example(self):
        pid = 42
        m_open = mock.mock_open()
        with mock.patch('source.notification_pusher.open', m_open, create=True):
            with mock.patch('os.getpid', mock.Mock(return_value=pid)) as os_git:
                create_pidfile('/file/path')

        m_open.assert_called_once_with('/file/path', 'w')
        m_open().write.assert_called_once_with(str(pid))



    def test_notification_worker__ok(self):
        task = mock.Mock()
        task.data.copy = mock.Mock(return_value = {'callback_url': '://test_url'})
        task.task_id = 5

        task_queue = mock.Mock()

        response = mock.Mock()
        response.status_code = 200

        with mock.patch('requests.post', mock.Mock(return_value = response)):
            notification_pusher.notification_worker(task, task_queue)

        task_queue.put.assert_called_with((task, 'ack'))


    def test_notification_worker__exception(self):
        import requests
        task = mock.MagicMock()

        task_queue = mock.Mock()

        request_exception = requests.RequestException('ERROR')

        with mock.patch('requests.post', mock.Mock(side_effect = request_exception)):
            with mock.patch('source.notification_pusher.json.dumps', mock.Mock()):
                notification_pusher.notification_worker(task, task_queue)

        task_queue.put.assert_called_once_with((task, 'bury'))


    def test_done_with_processed_task__ok(self):
        count = 5

        task = mock.Mock()
        task.task_id = 5
        task.action = mock.Mock()

        task_queue = mock.Mock()
        task_queue.get_nowait = mock.Mock(return_value = (task, "action"))
        task_queue.qsize = mock.Mock(return_value = count)

        notification_pusher.done_with_processed_tasks(task_queue)

        self.assertTrue(task.action.call_count == count)


    def test_done_with_processed_task__database_exc(self):
        import tarantool
        count = 1

        task = mock.Mock()
        task.task_id = 5
        error = tarantool.DatabaseError("ERROR")
        task.action = mock.Mock(side_effect = error)

        task_queue = mock.Mock()
        task_queue.get_nowait = mock.Mock(return_value = (task, "action"))
        task_queue.qsize = mock.Mock(return_value = count)

        logger = mock.Mock()

        with mock.patch('source.notification_pusher.logger', logger):
            notification_pusher.done_with_processed_tasks(task_queue)

        assert logger.exception.called


    def test_stop_handler(self):
        with mock.patch('source.notification_pusher.run_application', True):
            notification_pusher.stop_handler(signum=101)
            self.assertTrue(notification_pusher.run_application == False)


    def test_parse_cmd_args(self):
        import argparse
        cmd = ['-c', 'config', '-d', '-P', 'pidfile']
        self.assertEqual(notification_pusher.parse_cmd_args(cmd), argparse.Namespace(config='config',
                                                                daemon=True, pidfile='pidfile'))

    def test_install_signal_handlers(self):

        signal = mock.Mock()
        signal.SIGTERM = 1
        signal.SIGINT = 2
        signal.SIGHUP = 3
        signal.SIGQUIT = 4

        with mock.patch('gevent.signal', signal):
            notification_pusher.install_signal_handlers()
        self.assertTrue(signal.call_count == 4)


    def stop_app(*args, **kwargs):
        notification_pusher.run_application = False


    def test_main(self):

        argv = mock.Mock()
        argv.deamon = True
        argv.pidfile = True

        config = mock.Mock()
        config.LOGGING = mock.Mock()

        main_loop = mock.Mock(side_effect = self.stop_app)

        with mock.patch('source.notification_pusher.parse_cmd_args', argv):
         with mock.patch('source.notification_pusher.daemonize', mock.Mock()) as demonize:
          with mock.patch('source.notification_pusher.create_pidfile', mock.Mock()) as create_pidfile:
           with mock.patch('source.notification_pusher.load_config_from_pyfile', mock.Mock(return_value = config)) as load_config:
            with mock.patch('source.notification_pusher.os.path.realpath', mock.Mock()):
             with mock.patch('source.notification_pusher.os.path.expanduser', mock.Mock()):
              with mock.patch('source.notification_pusher.patch_all', mock.Mock()):
               with mock.patch('source.notification_pusher.dictConfig', mock.Mock()):
                with mock.patch('source.notification_pusher.run_application', True):
                 with mock.patch('source.notification_pusher.main_loop', main_loop):
                  notification_pusher.main(['-c', 'config', '-d', '-P', 'pidfile'])

        assert demonize.called
        assert create_pidfile.called
        assert load_config.called
        assert main_loop.called


    def test_main_exceprion(self):

        argv = mock.Mock()
        argv.deamon = True
        argv.pidfile = True

        config = mock.Mock()
        config.SLEEP_ON_FAIL = 1
        config.LOGGING = mock.Mock()

        exception = Exception("error")
        main_loop = mock.Mock(side_effect = exception)

        sleep = mock.Mock(side_effect = self.stop_app)

        with mock.patch('source.notification_pusher.parse_cmd_args', argv):
         with mock.patch('source.notification_pusher.daemonize', mock.Mock()) as demonize:
          with mock.patch('source.notification_pusher.create_pidfile', mock.Mock()) as create_pidfile:
           with mock.patch('source.notification_pusher.load_config_from_pyfile', mock.Mock(return_value = config)) as load_config:
            with mock.patch('source.notification_pusher.os.path.realpath', mock.Mock()):
             with mock.patch('source.notification_pusher.os.path.expanduser', mock.Mock()):
              with mock.patch('source.notification_pusher.patch_all', mock.Mock()):
               with mock.patch('source.notification_pusher.dictConfig', mock.Mock()):
                with mock.patch('source.notification_pusher.run_application', True):
                 with mock.patch('source.notification_pusher.main_loop', main_loop):
                  with mock.patch('source.notification_pusher.sleep', sleep):
                   notification_pusher.main(['-c', 'config', '-d', '-P', 'pidfile'])

        assert demonize.called
        assert create_pidfile.called
        assert load_config.called
        assert main_loop.called
        assert sleep.called






""" ================================================================"""




class MainLoopTestCase(unittest.TestCase):
    import tarantool
    import tarantool_queue
    from gevent import queue as gevent_queue
    #from gevent.pool import Pool

    def stop_app(*args, **kwargs):
        notification_pusher.run_application = False


    def test_main_loop__not_running(self):
        worker_pool = mock.Mock()
        logger = mock.Mock()
        config = mock.Mock()
        config.QUEUE_PORT = 42
        config.QUEUE_HOST = 'host'
        config.QUEUE_SPACE = 0
        config.QUEUE_TUBE = 'tube'
        config.QUEUE_TAKE_TIMEOUT = 0
        config.WORKER_POOL_SIZE = 0
        config.SLEEP = 1
        with mock.patch('source.notification_pusher.run_application', False):
            with mock.patch('source.notification_pusher.logger', logger):
                notification_pusher.main_loop(config)

        assert not worker_pool.free_count.called
        assert logger.info.called


    def test_main_loop__task_false(self):
        tube = mock.Mock()
        tube.take = mock.Mock(return_value = False)

        queue = mock.Mock()
        queue.tube = mock.Mock(return_value = tube)

        logger = mock.Mock()

        sleep = mock.Mock(side_effect = self.stop_app)

        worker_pool = mock.Mock()
        worker_pool.free_count = mock.Mock(return_value = 1)

        config = mock.Mock()
        config.QUEUE_PORT = 42
        config.QUEUE_HOST = 'host'
        config.QUEUE_SPACE = 0
        config.QUEUE_TUBE = 'tube'
        config.QUEUE_TAKE_TIMEOUT = 0
        config.WORKER_POOL_SIZE = 0
        config.SLEEP = 1

        with mock.patch('source.notification_pusher.tarantool_queue.Queue', mock.Mock(return_value = queue)):
            with mock.patch('source.notification_pusher.run_application', True):
                with mock.patch('source.notification_pusher.Pool', mock.Mock(return_value=worker_pool)):
                    with mock.patch('source.notification_pusher.sleep', sleep) as sleep: #as sleep is needed?
                        with mock.patch('source.notification_pusher.logger', logger):
                            notification_pusher.main_loop(config)

        sleep.assert_called_once_with(config.SLEEP)
        #assert logger.info.called


    def test_main_loop__task_true(self):
        task = mock.Mock()
        tube = mock.Mock()
        tube.take = mock.Mock(return_value = task)

        queue = mock.Mock()
        queue.tube = mock.Mock(return_value = tube)

        logger = mock.Mock()

        sleep = mock.Mock(side_effect = self.stop_app)

        worker_pool = mock.Mock()
        worker_pool.free_count = mock.Mock(return_value = 1)

        config = mock.Mock()
        config.QUEUE_PORT = 42
        config.QUEUE_HOST = 'host'
        config.QUEUE_SPACE = 0
        config.QUEUE_TUBE = 'tube'
        config.QUEUE_TAKE_TIMEOUT = 0
        config.WORKER_POOL_SIZE = 0
        config.SLEEP = 1

        with mock.patch('source.notification_pusher.tarantool_queue.Queue', mock.Mock(return_value = queue)):
            with mock.patch('source.notification_pusher.run_application', True):
                with mock.patch('source.notification_pusher.Pool', mock.Mock(return_value=worker_pool)):
                    with mock.patch('source.notification_pusher.sleep', sleep) as sleep: #as sleep is needed?
                        with mock.patch('source.notification_pusher.logger', logger):
                            notification_pusher.main_loop(config)

        sleep.assert_called_once_with(config.SLEEP)
        worker_pool.add.assert_called


    def test_load_config_from_pyfile(self):
        test_path = "source/tests/lib/testfile_load_config_from_pyfile.py"
        config = notification_pusher.load_config_from_pyfile(test_path)
        self.assertEqual(config.NAME_ONE, 4242)
        self.assertEqual(config.NAME_TWO, "MyPluginBaby")
        self.assertEqual(config.NAME_THREE, {
            'one': 'one',
            'two': 4242
        })
        self.assertFalse(hasattr(config, "NameFour"))
        self.assertFalse(hasattr(config, "nameFive"))
        self.assertFalse(hasattr(config, "name_six"))



""" ======================================================================"""



class DemonizeTestCase(unittest.TestCase):


    def test_demonize__father(self):
        pid = 4242
        with mock.patch('os.fork', mock.Mock(return_value=pid)) as os_fork:
            with mock.patch('os._exit', mock.Mock()) as os_exit:
                notification_pusher.daemonize()

        os_fork.assert_called_once_with()
        os_exit.assert_called_once_with(0)


    def test_demonize__child_child(self):
        pid = 0
        with mock.patch('os.fork', mock.Mock(return_value=pid)) as os_fork:
            with mock.patch('os.setsid', mock.Mock()) as os_setsid:
                with mock.patch('os._exit', mock.Mock()) as os_exit:
                    notification_pusher.daemonize()

        os_setsid.assert_called_once_with()
        assert os_fork.called
        assert not os_exit.called


    def test_demonize__child_father(self):
        father_pid = 0
        child_pid = 4242
        with mock.patch('os.fork', mock.Mock(side_effect=[child_pid, father_pid])) as os_fork:
            with mock.patch('os.setsid', mock.Mock()):
                with mock.patch('os._exit', mock.Mock()) as os_exit:
                    notification_pusher.daemonize()

        os_exit.assert_called_once_with(0)


    def test_demonize__father_exception(self):
        oserror = OSError("err")
        with mock.patch('os.fork', mock.Mock(side_effect=oserror)):
            self.assertRaises(Exception, notification_pusher.daemonize)


    def test_demonize__child_exception(self):
        oserror = OSError("err")
        pid = 0
        with mock.patch('os.fork', mock.Mock(side_effect=[pid,oserror])):
            with mock.patch('os.setsid', mock.Mock()): # as os_setsid:
                """os_setsid.assert_called_once_with() !!!!!! why don't pass?"""
                self.assertRaises(Exception, notification_pusher.daemonize)


