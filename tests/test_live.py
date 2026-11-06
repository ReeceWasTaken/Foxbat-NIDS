from app.live import CaptureManager

def test_initial_capture_state():
    state = CaptureManager().snapshot()
    assert state['running'] is False
    assert state['live_packets'] == 0
    assert state['traffic'] == []
