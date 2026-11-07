import subprocess, sys, unittest

class TestMachineInfo(unittest.TestCase):
    def test_script_runs_and_contains_fields(self):
        r = subprocess.run([sys.executable, "machine_info.py"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        for key in ["CPU", "Memory", "Disk", "OS", "Hostname", "Architecture"]:
            self.assertIn(key, r.stdout)

    def test_unknown_arg_rejected(self):
        r = subprocess.run([sys.executable, "machine_info.py", "--json"], capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("Traceback", r.stdout + r.stderr)

    def test_output_has_units(self):
        r = subprocess.run([sys.executable, "machine_info.py"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertTrue(any(u in r.stdout for u in ("GB", "MB", "bytes")))

if __name__ == "__main__":
    unittest.main()
