# -*- coding: utf-8 -*-
#!/usr/bin/python

import unittest
import mock
from source import lib


class InitTestCase(unittest.TestCase):
    def test_to_unicode_u(self):
        assert True == isinstance(lib.to_unicode(u'yandex'), unicode)

    def test_to_unicode_else(self):
        assert True == isinstance(lib.to_unicode('яндекс'), unicode)

    def test_to_str_u(self):
        assert True == isinstance(lib.to_str(u'yandex'), str)

    def test_to_str_else(self):
        assert True == isinstance(lib.to_str('яндекс'), str)

    def test_get_counters(self):
        self.assertEqual(['YA_METRICA'], lib.get_counters('mc.yandex.ru/metrika/watch.js'))

    def test_get_counters_not_counters(self):
        self.assertEqual([], lib.get_counters(''))

    def test_check_for_meta_not_result(self):
        soup = mock.Mock()
        soup.find = mock.Mock(return_value=False)

        with mock.patch('source.lib.BeautifulSoup', mock.Mock(return_value=soup)):
            assert None == lib.check_for_meta(mock.Mock(), mock.Mock())

    def test_check_for_meta_not_attr(self):
        result = mock.MagicMock()
        soup = mock.Mock()
        soup.find = mock.Mock(return_value=result)

        with mock.patch('source.lib.BeautifulSoup', mock.Mock(return_value=soup)):
            assert None == lib.check_for_meta(mock.Mock(), mock.Mock())

    def test_check_for_meta_not_http_equiv(self):
        result = mock.MagicMock()
        result.attrs = {
            'content': 'blah-blah-blah',
        }
        soup = mock.Mock()
        soup.find = mock.Mock(return_value=result)

        with mock.patch('source.lib.BeautifulSoup', mock.Mock(return_value=soup)):
            assert None == lib.check_for_meta(mock.Mock(), mock.Mock())

    def test_check_for_meta_error_in_len_splitted(self):
        content = '<meta http-equiv="refresh" content="">'
        assert None == lib.check_for_meta(content, mock.Mock())

    def test_check_for_meta_not_m(self):
        content = '<meta http-equiv="refresh" content="42; url=">'
        assert None == lib.check_for_meta(content, mock.Mock())

    def test_check_for_meta(self):
        content = '<meta http-equiv="refresh" content="42; url=www.yandex.ru">'

        with mock.patch('source.lib.urljoin', mock.Mock()) as urljoin:
            lib.check_for_meta(content, mock.Mock())

        assert True == urljoin.called

    def test_fix_market_url(self):
        self.assertEqual('http://play.google.com/store/apps/yandex', lib.fix_market_url('market:yandex'))

    def test_make_pycurl_request_not_redirect_url(self):
        buff = mock.Mock()
        buff.getvalue = mock.Mock()
        curl = mock.MagicMock()
        curl.getinfo = mock.Mock(return_value=None)

        with mock.patch('source.lib.to_str', mock.Mock()):
            with mock.patch('source.lib.prepare_url', mock.Mock()):
                with mock.patch('source.lib.StringIO', mock.Mock(return_value=buff)):
                    with mock.patch('source.lib.pycurl.Curl', mock.Mock(return_value=curl)):
                        with mock.patch('source.lib.to_unicode', mock.Mock()) as to_u:
                            lib.make_pycurl_request(mock.Mock(), 30)

        assert False == to_u.called

    def test_make_pycurl_request(self):
        buff = mock.Mock()
        buff.getvalue = mock.Mock()
        curl = mock.MagicMock()
        curl.getinfo = mock.Mock(return_value="www.mail.ru")

        with mock.patch('source.lib.to_str', mock.Mock()):
            with mock.patch('source.lib.prepare_url', mock.Mock()):
                with mock.patch('source.lib.StringIO', mock.Mock(return_value=buff)):
                    with mock.patch('source.lib.pycurl.Curl', mock.Mock(return_value=curl)):
                        with mock.patch('source.lib.to_unicode', mock.Mock()) as to_u:
                            lib.make_pycurl_request(mock.Mock(), 30, mock.Mock())

        assert True == to_u.called

    def test_get_url_error(self):
        with mock.patch('source.lib.make_pycurl_request', mock.Mock(side_effect=ValueError)):
            with mock.patch('source.lib.logger', mock.Mock()) as logger:
                lib.get_url(mock.Mock(), 30)

        assert True == logger.error.called

    def test_get_url_ok_redirect(self):
        with mock.patch('source.lib.make_pycurl_request', mock.Mock(return_value=[[], 'http://www.odnoklassniki.ru/yandexst.redirect'])):
            new_redirect_url, redirect_type, content = lib.get_url(mock.Mock(), 30)

        assert None == new_redirect_url

    def test_get_url_new_redirect_url(self):
        from source.lib import REDIRECT_HTTP
        with mock.patch('source.lib.make_pycurl_request', mock.Mock(return_value=[[], 'www.yandex.ru'])):
            with mock.patch('source.lib.fix_market_url', mock.Mock()) as fix_market_url:
                new_redirect_url, redirect_type, content = lib.get_url(mock.Mock(), 30)

        assert REDIRECT_HTTP == redirect_type
        assert False == fix_market_url.called

    def test_get_url_not_new_redirect_url_new_redirect_url(self):
        from source.lib import REDIRECT_META
        with mock.patch('source.lib.make_pycurl_request', mock.Mock(return_value=[[], False])):
            with mock.patch('source.lib.check_for_meta', mock.Mock(return_value='market:yandex.ru')):
                with mock.patch('source.lib.fix_market_url', mock.Mock()) as fix_market_url:
                    with mock.patch('source.lib.prepare_url', mock.Mock()):
                        new_redirect_url, redirect_type, content = lib.get_url(mock.Mock(), 30)

        assert REDIRECT_META == redirect_type
        assert True == fix_market_url.called

    def test_get_url_not_new_redirect_url_not_new_redirect_url(self):
        with mock.patch('source.lib.make_pycurl_request', mock.Mock(return_value=[[], False])):
            with mock.patch('source.lib.check_for_meta', mock.Mock(return_value=None)):
                new_redirect_url, redirect_type, content = lib.get_url(mock.Mock(), 30)

        assert None == redirect_type

    def test_get_redirect_history_mm_or_ok_url(self):
        url = 'http://odnoklassniki.ru/'

        with mock.patch('source.lib.prepare_url', mock.Mock(return_value=url)):
            with mock.patch('source.lib.get_counters', mock.Mock()) as get_counters:
                lib.get_redirect_history(url, 30)

        assert False == get_counters.called

    def test_get_redirect_history_not_redirect_url(self):
        url = 'www.yandex.ru'

        with mock.patch('source.lib.prepare_url', mock.Mock(return_value=url)):
            with mock.patch('source.lib.get_url', mock.Mock(return_value=[False, [], True])):
                with mock.patch('source.lib.get_counters', mock.Mock(return_value='counters')):
                    history_types, history_urls, counters = lib.get_redirect_history(url, 30)

        assert 0 == len(history_types)
        self.assertEqual('counters', counters)

    def test_get_redirect_history_redirect_type_error(self):
        url = 'www.yandex.ru'

        with mock.patch('source.lib.prepare_url', mock.Mock(return_value=url)):
            with mock.patch('source.lib.get_url', mock.Mock(return_value=[True, 'ERROR', False])):
                with mock.patch('source.lib.get_counters', mock.Mock()) as get_counters:
                    history_types, history_urls, counters = lib.get_redirect_history(url, 30)

        assert False == get_counters.called
        self.assertEqual(['ERROR'], history_types)

    def test_get_redirect_history_len_history_urls_more_max_redirects(self):
        url = 'www.yandex.ru'

        with mock.patch('source.lib.prepare_url', mock.Mock(return_value=url)):
            with mock.patch('source.lib.get_url', mock.Mock(return_value=[True, [], False])):
                history_types, history_urls, counters = lib.get_redirect_history(url, 30, 1)

        assert len(history_urls) == 2

    def test_prepare_url_none(self):
        assert None == lib.prepare_url(None)

    def test_prepare_url(self):
        in_url = mock.Mock()

        with mock.patch('source.lib.urlparse', mock.Mock(return_value=[in_url] * 6)) as urlparse:
            with mock.patch('source.lib.to_str', mock.Mock()):
                with mock.patch('source.lib.quote', mock.Mock()) as quote:
                    with mock.patch('source.lib.quote_plus', mock.Mock()) as quote_plus:
                        with mock.patch('source.lib.urlunparse', mock.Mock()) as urlunparse:
                            lib.prepare_url(u'www.yandex.ru')

        assert True == urlparse.called
        assert True == quote.called
        assert True == quote_plus.called
        assert True == urlunparse.called

    def test_prepare_url_unicode_error(self):
        in_url = mock.Mock()
        in_url.encode = mock.Mock(side_effect=UnicodeError)

        with mock.patch('source.lib.urlparse', mock.Mock(return_value=[in_url] * 6)) as urlparse:
            with mock.patch('source.lib.to_str', mock.Mock()):
                with mock.patch('source.lib.quote', mock.Mock()) as quote:
                    with mock.patch('source.lib.quote_plus', mock.Mock()) as quote_plus:
                        with mock.patch('source.lib.urlunparse', mock.Mock()) as urlunparse:
                            lib.prepare_url(u'www.yandex.ru')

        assert True == urlparse.called
        assert True == quote.called
        assert True == quote_plus.called
        assert True == urlunparse.called
