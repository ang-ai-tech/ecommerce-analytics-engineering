"""Tests for the synthetic data generator (the dbt tests check the models)."""

import csv
from collections import Counter
from datetime import datetime

import pytest

from shopdata.generator import QA_EMAIL_DOMAIN, build, generate


@pytest.fixture(scope="module")
def tables():
    return build(seed=42)


def test_same_seed_gives_the_same_data():
    assert build(seed=7, customers=200) == build(seed=7, customers=200)


def test_different_seed_gives_different_data():
    assert build(seed=1, customers=200) != build(seed=2, customers=200)


def test_raw_ids_are_consistent(tables):
    customer_ids = {row["customer_id"] for row in tables["customers"]}
    order_ids = {row["order_id"] for row in tables["orders"]}
    product_ids = {row["product_id"] for row in tables["products"]}
    assert {row["customer_id"] for row in tables["orders"]} <= customer_ids
    assert {row["order_id"] for row in tables["order_items"]} == order_ids
    assert {row["product_id"] for row in tables["order_items"]} <= product_ids


def test_deliberate_data_quality_issues_are_present(tables):
    versions = Counter(row["customer_id"] for row in tables["customers"])
    duplicates = [customer for customer, count in versions.items() if count > 1]
    emails = [row["email"] for row in tables["customers"]]
    statuses = {row["status"] for row in tables["orders"]}
    assert duplicates, "some customers should appear twice"
    assert any(email != email.strip().lower() for email in emails), "some e-mails should be messy"
    assert {"completed", "Completed", "COMPLETE", "Canceled"} <= statuses
    assert any(email.endswith(QA_EMAIL_DOMAIN) for email in emails), "QA accounts expected"


def test_every_real_order_has_exactly_one_purchase_event(tables):
    qa_customers = {
        row["customer_id"] for row in tables["customers"] if row["email"].endswith(QA_EMAIL_DOMAIN)
    }
    real_orders = {r["order_id"] for r in tables["orders"] if r["customer_id"] not in qa_customers}
    purchases = Counter(
        e["order_id"] for e in tables["web_events"] if e["event_type"] == "purchase"
    )
    assert set(purchases) == real_orders
    assert set(purchases.values()) == {1}


def test_purchase_event_happens_at_order_time(tables):
    ordered_at = {row["order_id"]: row["ordered_at"] for row in tables["orders"]}
    for event in tables["web_events"]:
        if event["event_type"] == "purchase":
            assert event["event_at"] == ordered_at[event["order_id"]]


def test_price_paid_is_stored_on_the_order_item(tables):
    """Prices changed in 2026, so the same product was sold at two different prices."""
    prices = {}
    for item in tables["order_items"]:
        prices.setdefault(item["product_id"], set()).add(item["unit_price"])
    assert any(len(values) > 1 for values in prices.values())


def test_until_keeps_only_data_known_at_that_date(tmp_path):
    until = datetime(2025, 6, 30, 23, 59, 59)
    generate(tmp_path, seed=42, until=until)

    with (tmp_path / "orders.csv").open(encoding="utf-8") as handle:
        orders = list(csv.DictReader(handle))
    with (tmp_path / "order_items.csv").open(encoding="utf-8") as handle:
        items = list(csv.DictReader(handle))
    assert orders and max(row["ordered_at"] for row in orders) <= "2025-06-30 23:59:59"
    assert {row["order_id"] for row in items} == {row["order_id"] for row in orders}


def test_csv_files_are_written(tmp_path):
    counts = generate(tmp_path, seed=42)
    assert set(counts) == {"customers", "products", "orders", "order_items", "web_events"}
    assert all(count > 0 for count in counts.values())
    assert (tmp_path / "web_events.csv").read_text(encoding="utf-8").startswith("event_id,")
