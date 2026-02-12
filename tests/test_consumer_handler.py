from src.services.consumer.handler import lambda_handler


def test_consumer_processes_records() -> None:
    event = {
        "Records": [
            {"messageId": "m-1", "body": '{"event_id":"e-1"}'},
            {"messageId": "m-2", "body": '{"event_id":"e-2"}'},
        ]
    }

    response = lambda_handler(event, None)

    assert response["processed_count"] == 2
    assert response["processed_records"][0]["message_id"] == "m-1"

