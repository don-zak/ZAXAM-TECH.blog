from pathlib import Path

PAGE = Path("maestro-demo-v5.html")


def _source() -> str:
    return PAGE.read_text(encoding="utf-8")


def test_v5_wrapper_declares_v5_release_identity() -> None:
    source = _source()

    assert "Maestro — Interactive Governance Demo v5" in source
    assert 'data-maestro-demo-release="v5"' in source
    assert 'title="Maestro interactive governance demo v5"' in source
    assert "Public showcase · v5" in source


def test_v5_removes_startup_tunisia_from_rendered_demo() -> None:
    source = _source()

    assert "normalizeV5Identity(doc)" in source
    assert ".replace(/Startup Tunisia\\s*/gi,'')" in source
    assert ".replace(/Public showcase\\s*·\\s*v4/gi,'Public showcase · v5')" in source
    assert "Interactive Governance Demo<br>Agentic Operations & Governance Control Plane<br>Public showcase · v5" in source


def test_v5_hides_embedded_legacy_shell_until_identity_is_normalized() -> None:
    source = _source()

    assert "iframe{border:0;width:100%;height:100%;display:block;background:#050a12;visibility:hidden}" in source
    assert "iframe.ready{visibility:visible}" in source
    assert source.index("normalizeV5Identity(doc);") < source.index("frame.classList.add('ready');")


def test_v5_cache_identity_no_longer_advertises_v4_release() -> None:
    source = _source()

    assert 'src="maestro-demo-v4.html?v=5-shell"' in source
    assert "?v=4-lifecycle-fix" not in source
    assert "Public showcase · v4" not in source
