import httpx
import respx
import prc

@respx.mock
def test_app_headers(v2_payload: dict, respx_mock: respx.MockRouter):
    route = respx_mock.post("https://api.erlc.gg/v2/server/command").respond(200,
        headers={"x-ratelimit-remaining":"10", "x-ratelimit-reset":"9999999"},
        json=v2_payload
    )
    
    with prc.v2.Client(
        global_key="global-key", app_id=123,
        use_registry=False, wait_for_rate_limit=False
    ) as app:
        assert app.is_public is True
        
        response = app.send_command(":h Hello World!", server_key="server-key")
        assert route.called
        assert isinstance(app.connection, httpx.Client)
        
        assert app.connection.headers.get("Authorization") == "global-key"
        assert response.request.headers.get("server-key") == "server-key"
        
def test_authorization_link():
    with prc.v2.Client(
        global_key="global-key", app_id=123,
        use_registry=False, wait_for_rate_limit=False
    ) as app:
        link = app.generate_auth_link(server_key="secret-serverkey")
        assert link == "https://api.erlc.gg/server-owners/server/serverkey/authorize/123"
