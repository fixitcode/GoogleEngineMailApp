
import mock
import pytest
import webtest

import main


@pytest.fixture
def app():
    return webtest.TestApp(main.app)


def test_get(app):
    response = app.get('/')
    assert response.status_int == 200


@mock.patch('python_http_client.client.Client._make_request')
def test_post(make_request_mock, app):
    response = mock.Mock()
    response.getcode.return_value = 200
    response.read.return_value = 'OK'
    response.info.return_value = {}
    make_request_mock.return_value = response

    app.post('/send', {
        'recipient': 'user@example.com'
    })

    assert make_request_mock.called
    request = make_request_mock.call_args[0][1]
    assert 'user@example.com' in request.data
