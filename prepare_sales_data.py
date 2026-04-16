from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path


def parse_price(price_str: str) -> Decimal:
    # Input prices look like "$3.00"
    return Decimal(price_str.replace("$", "").strip())


def main() -> None:
    repo_root = Path(__file__).resolve().parent
    input_dir = repo_root / "data"

    input_files = [
        input_dir / "daily_sales_data_0.csv",
        input_dir / "daily_sales_data_1.csv",
        input_dir / "daily_sales_data_2.csv",
    ]

    output_file = repo_root / "sales_data.csv"

    with output_file.open("w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["Sales", "Date", "Region"])

        for input_path in input_files:
            with input_path.open("r", newline="", encoding="utf-8") as f_in:
                reader = csv.DictReader(f_in)
                for row in reader:
                    product = (row.get("product") or "").strip().lower()
                    if product != "pink morsel":
                        continue

                    price = parse_price(row["price"])
                    quantity = int(row["quantity"])
                    sales = price * quantity

                    writer.writerow(
                        [
                            f"{sales:.2f}",
                            row["date"],
                            row["region"],
                        ]
                    )

    print(f"Wrote {output_file}")


if __name__ == "__main__":
    main()

