"""Source-level regression guards for behavior-sensitive ABHEDYA contracts.

These tests intentionally avoid importing the ML stack so they can run in a lightweight
CI environment. They protect constants and interface defaults that should not change as
part of repository cleanup or refactoring.
"""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read_source(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class HybridDecisionContractTests(unittest.TestCase):
    def test_ensemble_weights_remain_unchanged(self):
        source = read_source("backend/hybrid_decision.py")
        self.assertIn("0.4 * xgb_score", source)
        self.assertIn("0.4 * cnn_score", source)
        self.assertIn("0.2 * dqn_score", source)

    def test_dynamic_threshold_fallback_remains_065(self):
        source = read_source("backend/hybrid_decision.py")
        self.assertIn("return 0.65", source)
        self.assertIn("final_score >= THRESH", source)

    def test_honeypot_trigger_topic_remains_stable(self):
        source = read_source("backend/hybrid_decision.py")
        self.assertIn('producer.send("honeypot_triggers"', source)


class KafkaPipelineContractTests(unittest.TestCase):
    def test_default_topics_remain_stable(self):
        source = read_source("kafka_models_consumer.py")
        self.assertIn('"network-traffic"', source)
        self.assertIn('"predictions"', source)
        self.assertIn('"honeypot_triggers"', source)

    def test_default_database_remains_stable(self):
        source = read_source("kafka_models_consumer.py")
        self.assertIn('os.environ.get("SQLITE_DB", "cyber_defense.db")', source)

    def test_honeypot_response_action_remains_stable(self):
        source = read_source("kafka_models_consumer.py")
        self.assertIn('action = "send_to_honeypot"', source)

    def test_log_hmac_key_is_runtime_configurable(self):
        source = read_source("kafka_models_consumer.py")
        self.assertIn("ABHEDYA_LOG_HMAC_KEY", source)
        self.assertIn('LOG_HMAC_KEY = "supersecretkey"', source)


class ProducerContractTests(unittest.TestCase):
    def test_local_kafka_default_is_preserved(self):
        source = read_source("producer.py")
        self.assertIn('DEFAULT_KAFKA_BOOTSTRAP = "localhost:9092"', source)

    def test_kafka_override_is_supported(self):
        source = read_source("producer.py")
        self.assertIn('os.environ.get("KAFKA_BOOTSTRAP"', source)


class HoneypotControllerContractTests(unittest.TestCase):
    def test_controller_targets_running_honeypot_default_port(self):
        source = read_source("honeypot_controller.py")
        self.assertIn('os.getenv("HONEYPOT_PORT", "5001")', source)

    def test_controller_validates_attacker_ip_before_routing(self):
        source = read_source("honeypot_controller.py")
        self.assertIn("ipaddress.ip_address", source)
        self.assertIn("attacker_ip = normalize_ip(raw_ip)", source)

    def test_response_action_contract_is_preserved(self):
        source = read_source("honeypot_controller.py")
        self.assertIn('"send_to_honeypot"', source)


if __name__ == "__main__":
    unittest.main()
