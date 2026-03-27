import argparse
import time
from pathlib import Path

import dask
import dask.dataframe as dd
import numpy as np
import pandas as pd
from dask.distributed import Client


DATA_DIR = Path("/app/benchmark_data")


def max_rss_mb() -> float:
    # Linux: ru_maxrss is in KB.
    import resource

    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def generate_part(part_idx: int, rows: int) -> str:
    rng = np.random.default_rng(5000 + part_idx)

    start = np.datetime64("2026-01-01")
    end = np.datetime64("2026-04-01")
    seconds = int((end - start) / np.timedelta64(1, "s"))

    order_ts = start + rng.integers(0, seconds, rows).astype("timedelta64[s]")
    region = rng.choice(["Norte", "Sur", "Centro", "Occidente"], size=rows)
    category = rng.choice(["Tecnologia", "Hogar", "Deportes", "Moda"], size=rows)
    customer_id = rng.integers(1, 250_000, size=rows)
    units = rng.integers(1, 10, size=rows)
    unit_price = rng.uniform(10, 700, size=rows).round(2)
    discount = rng.choice([0.0, 0.05, 0.1, 0.15, 0.2], size=rows, p=[0.4, 0.2, 0.2, 0.15, 0.05])
    shipping_cost = rng.uniform(1, 30, size=rows).round(2)

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

    out = DATA_DIR / f"part_{part_idx:02d}.csv"
    df.to_csv(out, index=False)
    return str(out)


def ensure_data(parts: int, rows_per_part: int, rebuild: bool) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    existing = sorted(DATA_DIR.glob("part_*.csv"))
    if rebuild or len(existing) != parts:
        for f in existing:
            f.unlink()
        writes = [dask.delayed(generate_part)(i, rows_per_part) for i in range(parts)]
        dask.compute(*writes)


def run_dask(cluster_addr: str) -> dict:
    t0 = time.perf_counter()
    client = Client(cluster_addr)

    ddf = dd.read_csv(f"{DATA_DIR}/part_*.csv", blocksize=None)
    ddf["order_ts"] = dd.to_datetime(ddf["order_ts"])
    ddf["gross_sales"] = ddf["units"] * ddf["unit_price"]
    ddf["net_sales"] = ddf["gross_sales"] * (1 - ddf["discount"])
    ddf["profit"] = ddf["net_sales"] - ddf["shipping_cost"] - (0.55 * ddf["gross_sales"])
    ddf["is_high_value"] = ddf["net_sales"] > 1200

    # Shuffle deliberately to show distributed pressure.
    ddf = ddf.set_index("order_ts").persist()

    by_region = ddf.groupby("region")[["net_sales", "profit"]].sum()
    by_cat = ddf.groupby(["region", "category"])[["net_sales", "profit"]].mean()
    hourly = ddf["units"].resample("1h").sum()
    high_value = ddf.groupby("region")["is_high_value"].mean()

    dask.compute(by_region, by_cat, hourly, high_value)
    elapsed = time.perf_counter() - t0

    info = client.scheduler_info()
    workers = info.get("workers", {})
    worker_mem_mb = sum(w.get("metrics", {}).get("memory", 0) for w in workers.values()) / (1024**2)
    client.close()
    return {"elapsed_s": elapsed, "workers": len(workers), "worker_mem_mb": worker_mem_mb}


def run_pandas() -> dict:
    t0 = time.perf_counter()
    files = sorted(DATA_DIR.glob("part_*.csv"))
    df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)

    df["order_ts"] = pd.to_datetime(df["order_ts"])
    df["gross_sales"] = df["units"] * df["unit_price"]
    df["net_sales"] = df["gross_sales"] * (1 - df["discount"])
    df["profit"] = df["net_sales"] - df["shipping_cost"] - (0.55 * df["gross_sales"])
    df["is_high_value"] = df["net_sales"] > 1200

    df = df.set_index("order_ts")
    df.groupby("region")[["net_sales", "profit"]].sum()
    df.groupby(["region", "category"])[["net_sales", "profit"]].mean()
    df["units"].resample("1h").sum()
    df.groupby("region")["is_high_value"].mean()

    elapsed = time.perf_counter() - t0
    df_mem_mb = df.memory_usage(deep=True).sum() / (1024**2)
    proc_peak_mb = max_rss_mb()
    return {"elapsed_s": elapsed, "df_mem_mb": df_mem_mb, "proc_peak_mb": proc_peak_mb}


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark simple: Pandas vs Dask")
    parser.add_argument("--parts", type=int, default=6, help="Numero de archivos/particiones")
    parser.add_argument("--rows-per-part", type=int, default=250_000, help="Filas por particion")
    parser.add_argument("--cluster", default="tcp://dask-scheduler:8786", help="Direccion del scheduler Dask")
    parser.add_argument("--rebuild-data", action="store_true", help="Regenera archivos CSV")
    parser.add_argument("--skip-pandas", action="store_true", help="No corre benchmark de Pandas")
    parser.add_argument("--skip-dask", action="store_true", help="No corre benchmark de Dask")
    args = parser.parse_args()

    total_rows = args.parts * args.rows_per_part
    print(f"Dataset objetivo: {args.parts} partes x {args.rows_per_part:,} filas = {total_rows:,} filas")
    ensure_data(args.parts, args.rows_per_part, rebuild=args.rebuild_data)

    if not args.skip_pandas:
        p = run_pandas()
        print("\n[PANDAS]")
        print(f"Tiempo total: {p['elapsed_s']:.2f} s")
        print(f"Memoria DataFrame aprox: {p['df_mem_mb']:.1f} MB")
        print(f"Pico proceso (RSS): {p['proc_peak_mb']:.1f} MB")

    if not args.skip_dask:
        d = run_dask(args.cluster)
        print("\n[DASK]")
        print(f"Tiempo total: {d['elapsed_s']:.2f} s")
        print(f"Workers detectados: {d['workers']}")
        print(f"Memoria agregada workers (instante final): {d['worker_mem_mb']:.1f} MB")

    print("\nTip: mira Task Stream y Workers en http://localhost:8787 mientras corre Dask.")


if __name__ == "__main__":
    main()
