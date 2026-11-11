"""Start cFS briefly and verify the stock application's startup events."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

runtime = Path('/workspace/cfs/build-native_std/exe/cpu1')
log_path = runtime.parent.parent / 'cpi-smoke.log'
result_path = runtime.parent.parent / 'cpi-smoke-result.json'
markers = ['CFE_ES_Main entering OPERATIONAL state', 'Sample App Initialized.']
process = None
passed = False

def interrupted(signum, frame):
    raise RuntimeError(f'Smoke check interrupted by signal {signum}')

signal.signal(signal.SIGTERM, interrupted)
try:
    if not (runtime / 'core-cpu1').is_file():
        raise RuntimeError('Missing core-cpu1: run the build command first')
    with log_path.open('w') as log:
        process = subprocess.Popen(
            ['stdbuf', '-oL', '-eL', './core-cpu1'], cwd=runtime,
            stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
        )
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            time.sleep(0.25)
            text = log_path.read_text(errors='replace')
            if process.poll() is not None:
                raise RuntimeError(f'cFS exited early with code {process.returncode}')
            if all(marker in text for marker in markers):
                # Ensure startup success is followed by a short stable period.
                time.sleep(2)
                if process.poll() is not None:
                    raise RuntimeError('cFS exited immediately after startup')
                passed = True
                break
        if not passed:
            raise RuntimeError('Timed out waiting for cFS operational and sample app events')
except (Exception, KeyboardInterrupt) as exc:
    passed = False
    print(str(exc), file=sys.stderr)
finally:
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    if process is not None:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
    text = log_path.read_text(errors='replace') if log_path.exists() else ''
    result = {
        'passed': passed,
        'checks': {marker: marker in text for marker in markers},
        'log': str(log_path),
        'scope': 'Startup and short liveness check; does not validate application behavior',
    }
    result_path.write_text(json.dumps(result, indent=2) + '\n')
    print(text)
    print(json.dumps(result, indent=2))
sys.exit(0 if passed else 1)
