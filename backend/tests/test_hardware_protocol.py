import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('command_protocol', Path(__file__).parents[2] / 'hardware/command_protocol.py')
protocol = importlib.util.module_from_spec(spec)
spec.loader.exec_module(protocol)


def test_boot_rejects_pump_start_and_auto_rejects_manual_start():
    command = dict(action='SET_PUMP', value='true')
    assert protocol.apply_command(command, 'manual', False, False) == ('manual', False, 'REJECTED')
    assert protocol.apply_command(command, 'auto', False, True) == ('auto', False, 'REJECTED')


def test_off_mode_and_pump_off_are_supported():
    assert protocol.apply_command(dict(action='SET_MODE', value='OFF'), 'auto', True, True) == ('off', False, 'APPLIED')
    assert protocol.apply_command(dict(action='SET_PUMP', value='false'), 'manual', True, False) == ('manual', False, 'APPLIED')


def test_valid_manual_command_and_invalid_command():
    assert protocol.apply_command(dict(action='SET_PUMP', value='true'), 'manual', False, True) == ('manual', True, 'APPLIED')
    assert protocol.apply_command(dict(action='SET_MODE', value='unknown'), 'auto', False, True)[2] == 'REJECTED'
