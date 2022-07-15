from pushunder import Application


def test_sync(mocker):
    app = Application("token", "user")
    r = mocker.Mock()
    mocker.patch("pushunder.app.requests.request", r)
    resp_mock = mocker.Mock()
    r.return_value = resp_mock
    resp_mock.json.return_value=dict(state=True)

    resp = app._sync_request("meth", "https://url", params=dict(a=1), data=dict(b=2))
    r.assert_called_once_with("meth", "https://url", params=dict(a=1), data=dict(b=2))
    resp_mock.raise_for_status.assert_called_once()
    assert resp == dict(state=True)

