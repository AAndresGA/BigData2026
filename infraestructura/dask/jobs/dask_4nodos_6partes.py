import os
import time
from pathlib import Path

import dask
import dask.dataframe as dd
import numpy as np
import pandas as pd
from dask.distributed import Client


BASE_DIR = Path("/app/distributed_sales_6parts")
N_PARTS = 6
ROWS_PER_PART = 120_000


def build_part(part_idx: int, rows: int) -> str:
    rng = np.random.default_rng(1000 + part_idx)

    start = np.datetime64("2026-01-01")
    end = np.datetime64("2026-03-01")
    seconds = int((end - start) / np.timedelta64(1, "s"))

    order_ts = start + rng.integers(0, seconds, rows).astype("timedelta64[s]")
    region = rng.choice(["Norte", "Sur", "Centro", "Occidente"], size=rows, p=[0.2, 0.25, 0.35, 0.2])
    category = rng.choice(["Tecnologia", "Hogar", "Deportes", "Moda"], size=rows, p=[0.3, 0.25, 0.2, 0.25])
    customer_id = rng.integers(1, 40001, size=rows)
    units = rng.integers(1, 8, size=rows)
    unit_price = rng.uniform(8, 450, size=rows).round(2)
    discount = rng.choice([0.0, 0.05, 0.10, 0.15, 0.20], size=rows, p=[0.4, 0.2, 0.2, 0.15, 0.05])
    shipping_cost = rng.uniform(1, 18, size=rows).round(2)

    df = pd.DataFrame(
        {
            "order_id": np.arange(part_idx * rows, (part_idx + 1) * rows),
            "order_ts": order_ts.astype("datetime64[s]"),
            "region": region,
            "category": category,
            "customer_id": customer_id,
            "units": units,
            "unit_price": unit_price,
            "discount": discount,
            "shipping_cost": shipping_cost,
        }
    )

    part_path = BASE_DIR / f"sales_part_{part_idx:02d}.csv"
    df.to_csv(part_path, index=False)
    # Sleep corto para que se vea el trabajo en el dashboard.
    time.sleep(1.2)
    return str(part_path)


def main() -> None:
    client = Client("tcp://dask-scheduler:8786")
    print(f"Conectado al cluster: {client}")

    BASE_DIR.mkdir(parents=True, exist_ok=True)
    for old_file in BASE_DIR.glob("sales_part_*.csv"):
        old_file.unlink()

    delayed_writes = [dask.delayed(build_part)(i, ROWS_PER_PART) for i in range(N_PARTS)]
    written_files = dask.compute(*delayed_writes)
    print("Archivos generados:")
    for f in written_files:
        print(f" - {f}")

    ddf = dd.read_csv(f"{BASE_DIR}/sales_part_*.csv", blocksize=None)
    ddf["order_ts"] = dd.to_datetime(ddf["order_ts"])

    ddf["gross_sales"] = ddf["units"] * ddf["unit_price"]
    ddf["net_sales"] = ddf["gross_sales"] * (1 - ddf["discount"])
    ddf["profit"] = ddf["net_sales"] - ddf["shipping_cost"] - (0.55 * ddf["gross_sales"])
    ddf["is_high_value"] = ddf["net_sales"] > 600

    # Repartición por tiempo para inducir shuffle visible en dashboard.
    ddf = ddf.set_index("order_ts").persist()

    by_region = (
        ddf.groupby("region")[["net_sales", "profit", "units"]]
        .sum()
        .rename(columns={"net_sales": "ventas_netas", "profit": "utilidad", "units": "unidades"})
        .round(2)
    )

    by_category_region = (
        ddf.groupby(["region", "category"])[["net_sales", "profit"]]
        .mean()
        .rename(columns={"net_sales": "ticket_promedio", "profit": "utilidad_promedio"})
        .round(2)
    )

    hourly_demand = ddf["units"].resample("1h").sum().rename("demanda_horaria")
    high_value_rate = ddf.groupby("region")["is_high_value"].mean().rename("ratio_alto_valor")

    by_region_df, by_category_region_df, hourly_demand_df, high_value_rate_df = dask.compute(
        by_region, by_category_region, hourly_demand, high_value_rate
    )

    print("\n=== KPI por region ===")
    print(by_region_df.sort_values("ventas_netas", ascending=False))

    print("\n=== Ticket/Utilidad promedio por region y categoria (top 12) ===")
    print(by_category_region_df.sort_values("ticket_promedio", ascending=False).head(12))

    print("\n=== Demanda horaria (ultimas 12 horas) ===")
    print(hourly_demand_df.tail(12))

    print("\n=== Ratio de ordenes de alto valor por region ===")
    print((high_value_rate_df * 100).round(2).astype(str) + "%")

    print("\nListo. Dashboard: http://localhost:8787")


if __name__ == "__main__":
    main()
