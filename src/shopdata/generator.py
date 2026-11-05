"""Generate a synthetic e-commerce dataset, including deliberate data quality issues.

The data imitates raw exports from a fictional online store selling home and office
products in five European countries. Everything is random but reproducible (seeded).

Deliberate data quality issues, fixed later in the dbt staging layer:
- some customers appear twice in the export (an older and a newer version of the row);
- some e-mail addresses have upper-case letters or extra spaces;
- order statuses are written in several ways ("completed", "Completed", "COMPLETE"...);
- internal test orders placed by the QA team must be excluded from reporting.
"""

from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

START = datetime(2025, 1, 1)
END = datetime(2026, 9, 30, 23, 59, 59)
PRICE_CHANGE_DATE = datetime(2026, 1, 1)
PRICE_INCREASE = 1.08  # some categories become 8% more expensive in 2026

COUNTRIES = {"IT": 0.30, "DE": 0.25, "FR": 0.20, "ES": 0.15, "NL": 0.10}
CHANNELS = {"web": 0.70, "app": 0.30}
STATUS_WEIGHTS = {"completed": 0.90, "cancelled": 0.06, "refunded": 0.04}
STATUS_SPELLINGS = {
    "completed": ["completed", "Completed", "COMPLETE"],
    "cancelled": ["cancelled", "Canceled"],
    "refunded": ["refunded", "Refunded"],
}
QA_EMAIL_DOMAIN = "qa.example.com"

# product_id, name, category, price before 2026
PRODUCTS = [
    (1, "Ceramic mug set", "Kitchen", 24.90),
    (2, "Chef knife", "Kitchen", 59.00),
    (3, "Bamboo cutting board", "Kitchen", 19.90),
    (4, "Glass storage jars", "Kitchen", 29.90),
    (5, "Espresso cups", "Kitchen", 17.50),
    (6, "Desk lamp", "Lighting", 49.00),
    (7, "Floor lamp", "Lighting", 129.00),
    (8, "LED string lights", "Lighting", 14.90),
    (9, "Pendant light", "Lighting", 89.00),
    (10, "Notebook A5", "Office", 9.90),
    (11, "Desk organiser", "Office", 22.00),
    (12, "Ergonomic chair cushion", "Office", 39.90),
    (13, "Monitor stand", "Office", 45.00),
    (14, "Fountain pen", "Office", 34.00),
    (15, "Linen cushion cover", "Textiles", 18.90),
    (16, "Wool throw blanket", "Textiles", 69.00),
    (17, "Cotton bath towels", "Textiles", 32.00),
    (18, "Table runner", "Textiles", 21.50),
    (19, "Scented candle", "Decor", 16.90),
    (20, "Wall clock", "Decor", 42.00),
    (21, "Ceramic vase", "Decor", 27.50),
    (22, "Photo frame set", "Decor", 24.00),
    (23, "Indoor plant pot", "Decor", 19.00),
    (24, "Wall mirror", "Decor", 119.00),
]
CATEGORIES_WITH_PRICE_INCREASE = {"Kitchen", "Lighting"}
DISCONTINUED_PRODUCTS = {5, 18}
DISCONTINUED_FROM = datetime(2026, 4, 1)


@dataclass
class Customer:
    customer_id: int
    country_code: str
    created_at: datetime
    is_qa: bool = False


def _pick(rng: random.Random, weights: dict[str, float]) -> str:
    return rng.choices(list(weights), weights=list(weights.values()))[0]


def _ts(value: datetime) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%S")


def _random_moment(rng: random.Random) -> datetime:
    """A moment in the period; the store grows, so later moments are more likely."""
    share = rng.random() ** 0.6  # skewed towards the end of the period
    moment = START + (END - START) * share
    return moment.replace(hour=rng.choice(range(8, 24)), minute=rng.randint(0, 59))


def _price_on(product: tuple, moment: datetime) -> float:
    _, _, category, price = product
    if moment >= PRICE_CHANGE_DATE and category in CATEGORIES_WITH_PRICE_INCREASE:
        return round(price * PRICE_INCREASE, 2)
    return price


def _messy_email(rng: random.Random, email: str) -> str:
    roll = rng.random()
    if roll < 0.06:
        return email.upper()
    if roll < 0.10:
        return f"  {email} "
    return email


def build(seed: int = 42, customers: int = 3000) -> dict[str, list[dict]]:
    """Build all raw tables in memory."""
    rng = random.Random(seed)
    tables: dict[str, list[dict]] = {
        "customers": [],
        "products": [],
        "orders": [],
        "order_items": [],
        "web_events": [],
    }

    for product in PRODUCTS:
        product_id, name, category, _ = product
        tables["products"].append(
            {
                "product_id": product_id,
                "product_name": name,
                "category": category,
                "unit_price": f"{_price_on(product, END):.2f}",
                "is_active": "false" if product_id in DISCONTINUED_PRODUCTS else "true",
            }
        )

    people: list[Customer] = []
    for customer_id in range(1, customers + 1):
        created_at = _random_moment(rng)
        people.append(Customer(customer_id, _pick(rng, COUNTRIES), created_at))
    for n in range(1, 11):  # internal QA accounts
        people.append(Customer(customers + n, "IT", _random_moment(rng), is_qa=True))

    for person in people:
        if person.is_qa:
            email = f"tester{person.customer_id}@{QA_EMAIL_DOMAIN}"
        else:
            email = f"user{person.customer_id:05d}@example.com"
        row = {
            "customer_id": person.customer_id,
            "email": _messy_email(rng, email),
            "country_code": person.country_code,
            "created_at": _ts(person.created_at),
            "updated_at": _ts(person.created_at),
        }
        tables["customers"].append(row)
        if not person.is_qa and rng.random() < 0.03:
            # Duplicate: the export also contains a newer version of the same customer.
            updated_at = person.created_at + timedelta(days=rng.randint(1, 90))
            tables["customers"].append(dict(row, email=email, updated_at=_ts(updated_at)))

    order_moments: list[tuple[datetime, Customer]] = []
    for person in people:
        if not person.is_qa and rng.random() > 0.80:
            continue  # signed up but never ordered
        moment = person.created_at + timedelta(minutes=rng.randint(5, 14 * 24 * 60))
        while moment <= END:
            order_moments.append((moment, person))
            if rng.random() > 0.45:  # probability of ordering again
                break
            moment += timedelta(days=rng.expovariate(1 / 55), minutes=rng.randint(0, 600))
    order_moments.sort(key=lambda item: (item[0], item[1].customer_id))

    order_item_id = 0
    converting_sessions: list[tuple[datetime, int, int]] = []
    for order_id, (moment, person) in enumerate(order_moments, start=1):
        status = _pick(rng, STATUS_WEIGHTS)
        tables["orders"].append(
            {
                "order_id": order_id,
                "customer_id": person.customer_id,
                "ordered_at": _ts(moment),
                "status": rng.choice(STATUS_SPELLINGS[status]),
                "channel": "web" if person.is_qa else _pick(rng, CHANNELS),
            }
        )
        available = [
            p for p in PRODUCTS if moment < DISCONTINUED_FROM or p[0] not in DISCONTINUED_PRODUCTS
        ]
        for product in rng.sample(available, k=rng.choices([1, 2, 3, 4], [50, 30, 15, 5])[0]):
            order_item_id += 1
            tables["order_items"].append(
                {
                    "order_item_id": order_item_id,
                    "order_id": order_id,
                    "product_id": product[0],
                    "quantity": rng.choices([1, 2, 3], [80, 15, 5])[0],
                    "unit_price": f"{_price_on(product, moment):.2f}",
                }
            )
        if not person.is_qa:  # QA orders are entered in the back office, not on the site
            converting_sessions.append((moment, person.customer_id, order_id))

    events = _web_events(rng, people, converting_sessions)
    events.sort(key=lambda event: (event["event_at"], event["session_id"], event["step"]))
    for event_id, event in enumerate(events, start=1):
        del event["step"]
        tables["web_events"].append({"event_id": event_id, **event})
    return tables


def _web_events(
    rng: random.Random,
    people: list[Customer],
    converting_sessions: list[tuple[datetime, int, int]],
) -> list[dict]:
    """Website and app sessions: every order has a session, most sessions buy nothing."""
    events: list[dict] = []
    session_number = 0

    def add_session(moment: datetime, customer_id, steps: int, order_id=None, ends=False):
        """One session; with ends=True the last event happens exactly at `moment`."""
        nonlocal session_number
        session_number += 1
        names = ["page_view"] * rng.randint(1, 2)
        names += ["add_to_cart", "begin_checkout", "purchase"][: steps - 1]
        gaps = [timedelta(seconds=rng.randint(20, 240)) for _ in names[1:]]
        if ends:
            moment -= sum(gaps, timedelta())
        for step, name in enumerate(names):
            events.append(
                {
                    "session_id": f"S{session_number:06d}",
                    "customer_id": "" if customer_id is None else customer_id,
                    "event_type": name,
                    "event_at": _ts(moment),
                    "order_id": order_id if name == "purchase" else "",
                    "step": step,
                }
            )
            if step < len(gaps):
                moment += gaps[step]

    for moment, customer_id, order_id in converting_sessions:
        add_session(moment, customer_id, steps=4, order_id=order_id, ends=True)

    shoppers = [person for person in people if not person.is_qa]
    for _ in range(len(converting_sessions) * 8):
        start = _random_moment(rng).replace(second=rng.randint(0, 59))
        person = rng.choice(shoppers)
        logged_in = rng.random() < 0.4 and person.created_at <= start
        steps = rng.choices([1, 2, 3], [65, 22, 13])[0]  # where the visitor stops
        add_session(start, person.customer_id if logged_in else None, steps)
    return events


def write(
    tables: dict[str, list[dict]], out_dir: Path, until: datetime | None = None
) -> dict[str, int]:
    """Write the tables as CSV files, optionally only the data known at `until`."""
    out_dir.mkdir(parents=True, exist_ok=True)
    cutoff = _ts(until) if until else None
    time_column = {
        "customers": "updated_at",
        "orders": "ordered_at",
        "web_events": "event_at",
    }
    kept_orders: set[int] = set()
    counts = {}
    for name, rows in tables.items():
        if cutoff and name in time_column:
            rows = [row for row in rows if row[time_column[name]] <= cutoff]
        if cutoff and name == "orders":
            kept_orders = {row["order_id"] for row in rows}
        if cutoff and name == "order_items":
            rows = [row for row in rows if row["order_id"] in kept_orders]
        with (out_dir / f"{name}.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(tables[name][0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        counts[name] = len(rows)
    return counts


def generate(out_dir: Path, seed: int = 42, until: datetime | None = None) -> dict[str, int]:
    """Build and write the dataset; return the number of rows per table."""
    return write(build(seed), out_dir, until)
