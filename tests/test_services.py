import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from backend.repository import CsvRepository
from backend.simulation_service import SimulationService


class ServiceTests(unittest.TestCase):
    def test_simulation_produces_valid_snapshot_and_sensor_states(self):
        service = SimulationService()
        snapshot = service.next_snapshot()
        self.assertIn(snapshot.state, {"IDLE", "RUNNING", "PAUSED", "FAULT"})
        self.assertGreaterEqual(snapshot.total_output, 0)
        self.assertTrue(service.sensor_states())

    def test_csv_repository_appends_and_reads_date_partitioned_rows(self):
        with tempfile.TemporaryDirectory() as temporary:
            repository = CsvRepository(Path(temporary))
            repository.append_production({"timestamp": datetime.now().isoformat(), "output": 1, "ok": 1, "ng": 0, "yield": 100, "cycle_time": 18, "machine_state": "RUNNING", "work_order": "WO-1"})
            rows = repository.read_rows("production")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["work_order"], "WO-1")


if __name__ == "__main__":
    unittest.main()
