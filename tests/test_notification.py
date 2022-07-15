import pytest
from pushunder import Application


@pytest.fixture
def app(mocker):
    a = Application("token", "user")
    a._sync_push_msg = mocker.Mock()
    a._async_push_msg = mocker.AsyncMock()
    return a


# @pytest.mark.parametrize("priority", [
#     -2, -1, 0, 1, 2
# ])
# def test_priority(priority, app):
#     n = app.notification(priority=priority, title="title", message="msg")
#     n.send()
#     assert n.app._sync_push_msg.called_once_with()
