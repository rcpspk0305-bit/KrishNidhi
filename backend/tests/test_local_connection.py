import asyncio
import importlib.util
import json
from pathlib import Path

from app.services.sse_service import SSEBroadcaster


def test_device_streams_do_not_receive_other_devices():
    async def scenario():
        events = SSEBroadcaster()
        one = await events.subscribe('one')
        two = await events.subscribe('two')
        all_devices = await events.subscribe('all')
        await events.broadcast('telemetry', {'temperature': 27}, device_id='one')
        assert not one.empty()
        assert two.empty()
        assert not all_devices.empty()
        await events.unsubscribe(one, 'one')
        assert one not in events.listeners['one']
    asyncio.run(scenario())


def test_real_hardware_telemetry_reaches_dashboard_and_queue(client):
    from app.api.v1.device_compat import DEVICE_TOKEN
    headers = {'X-Device-Token': DEVICE_TOKEN, 'X-Device-Key': DEVICE_TOKEN}
    response = client.post('/api/device/telemetry', headers=headers, json={
        'device_id': 'usb-test', 'temperature_c': 27, 'humidity_pct': 39,
        'soil_moisture_pct': 0, 'pump_on': False, 'mode': 'off',
    })
    assert response.status_code == 200
    latest = client.get('/api/v1/devices/usb-test/telemetry/latest').json()
    assert latest['temperature'] == 27
    assert latest['soil_moisture'] == 0
    assert latest['control_mode'] == 'OFF'
    command = client.post('/api/v1/devices/usb-test/pump', json={
        'action': 'SET_MODE', 'value': 'MANUAL', 'ttl_seconds': 30,
    }).json()
    polled = client.get('/api/v1/devices/usb-test/commands', headers=headers).json()
    assert polled['command']['command_id'] == command['command_id']
    ack = client.post('/api/v1/devices/usb-test/commands/' + command['command_id'] + '/ack',
                      headers=headers, json={'status': 'APPLIED', 'confirmed_state': False})
    assert ack.status_code == 200
    assert not client.get('/api/v1/devices/usb-test/commands', headers=headers).json()['has_command']


def test_usb_bridge_parses_only_real_sensor_frames():
    import pytest
    spec = importlib.util.spec_from_file_location('usb_bridge', Path(__file__).parents[2] / 'hardware/usb_telemetry_bridge.py')
    bridge = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bridge)
    assert bridge.parse_reading('log\nUSB_TELEMETRY:' + json.dumps({'temperature_c': 27}))['temperature_c'] == 27
    with pytest.raises(ValueError):
        bridge.parse_reading('USB_TELEMETRY:{}')
