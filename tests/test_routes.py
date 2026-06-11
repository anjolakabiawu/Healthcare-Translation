import json


def test_languages_returns_200(client):
    res = client.get("/api/languages")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert "pairs" in data
    assert "languages" in data
    assert len(data["pairs"]) > 0


def test_history_empty_initially(client):
    res = client.get("/api/history")
    assert res.status_code == 200
    assert json.loads(res.data) == []


def test_history_delete(client):
    res = client.delete("/api/history")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert "message" in data


def test_translate_missing_fields(client):
    res = client.post(
        "/api/translate",
        data=json.dumps({"text": "hello"}),
        content_type="application/json",
    )
    assert res.status_code == 400


def test_translate_missing_text(client):
    res = client.post(
        "/api/translate",
        data=json.dumps({"source_lang": "en", "target_lang": "es"}),
        content_type="application/json",
    )
    assert res.status_code == 400


def test_translate_unsupported_pair(client):
    res = client.post(
        "/api/translate",
        data=json.dumps({"text": "hello", "source_lang": "en", "target_lang": "xx"}),
        content_type="application/json",
    )
    assert res.status_code == 400


def test_transcribe_no_data(client):
    res = client.post("/api/transcribe", data=b"", content_type="audio/wav")
    assert res.status_code == 400


def test_transcribe_too_large(client):
    big = b"x" * (11 * 1024 * 1024)
    res = client.post("/api/transcribe", data=big, content_type="audio/wav")
    assert res.status_code == 413


def test_index_returns_200(client):
    res = client.get("/")
    assert res.status_code == 200
