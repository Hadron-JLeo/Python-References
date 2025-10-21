# Remove hours and minutes when converting to datetime

df = df.with_columns(
    pl.col("BuyDate").cast(pl.Date)
)

# But more commonly:
buys = buys.with_columns(
    pl.col("BuyDate").str.strptime(pl.Date, "%Y-%m-%d") # instead of pl.Datetime
)


# DropNAS

buys = buys.drop_nulls(subset=["ID", "Date"])
