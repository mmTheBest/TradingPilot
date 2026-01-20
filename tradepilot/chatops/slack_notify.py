import httpx


def post_in_channel(response_url: str, text: str) -> None:
    httpx.post(response_url, json={"response_type": "in_channel", "text": text}, timeout=5.0)
