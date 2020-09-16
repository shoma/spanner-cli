from spannercli import config


def test_get_pygment_style_accept(monkeypatch):
    monkeypatch.setenv(config.EnvironmentVariables.PYGMENT_STYLE, "inkpot")
    ret = config.get_pygment_style()
    assert ret == 'inkpot'


def test_get_pygment_style_default():
    ret = config.get_pygment_style()
    assert ret == config.Constants.PYGMENT_STYLE


def test_get_pygment_style_fallback(monkeypatch):
    monkeypatch.setenv(config.EnvironmentVariables.PYGMENT_STYLE, "not_supported")
    ret = config.get_pygment_style()
    assert ret == config.Constants.PYGMENT_STYLE
