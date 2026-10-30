"""Pure command parsing shared by MicroPython firmware and host regression tests."""


def apply_command(command, mode, manual_requested, allow_pump_on):
    action, value = command.get('action'), command.get('value')
    if action == 'SET_MODE' and value in ('AUTO', 'MANUAL', 'OFF'):
        return value.lower(), False, 'APPLIED'
    if action == 'SET_PUMP' and str(value).lower() in ('true', 'false'):
        wanted = str(value).lower() == 'true'
        if wanted and (not allow_pump_on or mode != 'manual'):
            return mode, manual_requested, 'REJECTED'
        return mode, wanted, 'APPLIED'
    return mode, manual_requested, 'REJECTED'
