__author__ = 'Admin'

import unittest
import mock
from source.lib import worker

class WorkerTestCase(unittest.TestCase):

    def test_get_redirect_history_from_task_error_and_not_is_recheck(self):
        task = mock.MagicMock()
        task.data = {
            'url': u'www.yandex.ru',
            'is_recheck': False,
            'url_id': 1
        }
        with mock.patch('source.lib.worker.get_redirect_history', mock.Mock(return_value=['ERROR', '', ''])):
            is_input, data = worker.get_redirect_history_from_task(task, 30)

        assert True == is_input

    def test_get_redirect_history_from_else_if_suspicious(self):
        task = mock.MagicMock()
        task.data = {
            'url': u'www.yandex.ru',
            'is_recheck': False,
            'url_id': 1,
            'suspicious': 'blahblahblah'
        }
        with mock.patch('source.lib.worker.get_redirect_history', mock.Mock(return_value=['', '', ''])):
            is_input, data = worker.get_redirect_history_from_task(task, 30)

        assert False == is_input
        assert data['suspicious']

    def test_get_redirect_history_from_else_else(self):
        task = mock.MagicMock()
        task.data = {
            'url': u'www.yandex.ru',
            'is_recheck': False,
            'url_id': 1,
        }
        with mock.patch('source.lib.worker.get_redirect_history', mock.Mock(return_value=['', '', ''])):
            is_input, data = worker.get_redirect_history_from_task(task, 30)

        assert False == is_input
        assert False == data.has_key('suspicious')

    def test_worker_not_parent_proc(self):
        in_tube = mock.MagicMock()
        out_tube = mock.MagicMock()
        with mock.patch('source.lib.worker.get_tube', mock.Mock(side_effect=[in_tube,out_tube])):
            with mock.patch('os.path.exists', mock.Mock(return_value=False)):
                worker.worker(mock.Mock(), 42)

        assert False == in_tube.called

    def test_worker_not_task(self):
        in_out_tube = mock.MagicMock()
        in_out_tube.take = mock.Mock(return_value=False)
        with mock.patch('source.lib.worker.get_tube', mock.Mock(return_value=in_out_tube)):
            with mock.patch('os.path.exists', mock.Mock(side_effect=[True, False])):
                with mock.patch('source.lib.worker.get_redirect_history_from_task', mock.Mock()) \
                        as redirect_history:
                    worker.worker(mock.Mock(), 42)

        assert False == redirect_history.called

    def test_worker_not_result(self):
        in_out_tube = mock.MagicMock()
        with mock.patch('source.lib.worker.get_tube', mock.Mock(return_value=in_out_tube)):
            with mock.patch('os.path.exists', mock.Mock(side_effect=[True, False])):
                with mock.patch('source.lib.worker.get_redirect_history_from_task', mock.Mock(return_value=False)):
                    with mock.patch("source.lib.worker.logger", mock.Mock()) as logger:
                        worker.worker(mock.Mock(), 42)

        assert False == logger.debug.called

    def test_worker_not_is_input_database_error(self):
        from source.lib.worker import DatabaseError
        task = mock.Mock()
        task.ack = mock.Mock(side_effect=DatabaseError)
        in_tube = mock.MagicMock()
        in_tube.take = mock.Mock(return_value=task)
        out_tube = mock.MagicMock()
        with mock.patch('source.lib.worker.get_tube', mock.Mock(side_effect=[in_tube, out_tube])):
            with mock.patch('os.path.exists', mock.Mock(side_effect=[True, False])):
                with mock.patch('source.lib.worker.get_redirect_history_from_task', mock.Mock(return_value=[False, ""])):
                    with mock.patch("source.lib.worker.logger", mock.Mock()) as logger:
                        worker.worker(mock.Mock(), 42)

        assert True == out_tube.put.called
        assert True == logger.exception.called

    def test_worker_is_input(self):
        in_tube = mock.MagicMock()
        out_tube = mock.MagicMock()
        with mock.patch('source.lib.worker.get_tube', mock.Mock(side_effect=[in_tube, out_tube])):
            with mock.patch('os.path.exists', mock.Mock(side_effect=[True, False])):
                with mock.patch('source.lib.worker.get_redirect_history_from_task', mock.Mock(return_value=[True, ""])):
                    worker.worker(mock.Mock(), 42)

        assert True == in_tube.put.called

