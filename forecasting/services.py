import logging
from datetime import date, timedelta
 
import pandas as pd
from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA
 
from .models import Forecast
from .queries import SalesQuery
 
 
logger = logging.getLogger(__name__)
 
MODEL_NAME = "AutoARIMA"
 
 
class InsufficientHistoryError(Exception):
    """Raised when a product doesn't have enough transaction history to forecast."""
 
 
class ForecastService:
 
    def get_or_create_forecast(self, product_id, horizon=30, force_refresh=False):
        if not force_refresh:
            cached = self._load_cached_forecast(
                product_id,
                horizon,
            )
 
            if cached:
                return cached
 
        return self._generate_forecast(
            product_id,
            horizon,
        )
 
 
    def get_summary(self, product_id, forecast):
        history = list(
            SalesQuery.product_daily_history(product_id)
        )
 
        demands = [
            row["demand"] or 0
            for row in history
        ]
 
        returns = [
            row["customer_return"] or 0
            for row in history
        ]
 
        bad_orders = [
            row["customer_bad_order"] or 0
            for row in history
        ]
 
        predictions = [
            row["predicted_quantity"]
            for row in forecast
        ]
 
        forecast_total = round(
            sum(predictions)
        )
 
        safety_stock = round(forecast_total * 0.10)
        
        return {
            "history_days": len(history),
 
            "total_units": sum(demands),
 
            "average_daily": round(
                sum(demands) / len(demands),
                2,
            ) if demands else 0,
 
            "highest_demand": max(demands)
            if demands else 0,
 
            "lowest_demand": min(demands)
            if demands else 0,
 
            "customer_returns": sum(returns),
 
            "customer_bad_orders": sum(bad_orders),
 
            "forecast_total": forecast_total,
 
            "forecast_average": round(
                forecast_total / len(predictions),
                2,
            ) if predictions else 0,
 
            "recommended_stock": forecast_total + safety_stock,
 
            "safety_stock": safety_stock,
 
            "last_transaction":
                SalesQuery.latest_transaction_date(
                    product_id
                ),
        }
 
 
    def _load_cached_forecast(self, product_id, horizon):
        today = date.today()
 
        target_end = today + timedelta(
            days=horizon
        )
 
        queryset = (
            Forecast.objects
            .filter(
                product_id=product_id,
                model_name=MODEL_NAME,
                generated_at__date=today,
                forecast_date__gte=today,
                # Without this, a cache generated earlier today with a
                # larger horizon would return *all* its rows regardless of
                # the horizon requested now, silently inflating
                # forecast_total / safety_stock / recommended_stock for
                # smaller-horizon requests made later the same day.
                forecast_date__lte=target_end,
            )
            .order_by("forecast_date")
        )
 
        latest = queryset.last()
 
        if not latest:
            return None
 
        if latest.forecast_date < (
            target_end - timedelta(days=1)
        ):
            return None
 
        return list(
            queryset.values(
                "forecast_date",
                "predicted_quantity",
                "lower_bound",
                "upper_bound",
            )
        )
 
 
    def _generate_forecast(self, product_id, horizon):
        history = list(
            SalesQuery.product_daily_history(product_id)
        )
 
        if not history:
            raise InsufficientHistoryError(
                "No historical data available."
            )
 
        if not any((row["demand"] or 0) for row in history):
            raise InsufficientHistoryError(
                "No net demand recorded; nothing to forecast."
            )
 
        dataframe = self._prepare_dataframe(
            history,
            product_id,
        )
 
        forecast_dataframe = self._run_model(
            dataframe,
            horizon,
        )
 
        rows = self._to_forecast_rows(
            forecast_dataframe,
            product_id,
        )
 
        self._save_forecast(
            product_id,
            rows,
        )
 
        return [
            {
                "forecast_date": row.forecast_date,
                "predicted_quantity": row.predicted_quantity,
                "lower_bound": row.lower_bound,
                "upper_bound": row.upper_bound,
            }
            for row in rows
        ]
 
 
    def _prepare_dataframe(self, history, product_id):
        dataframe = (
            pd.DataFrame(history)
            .rename(
                columns={
                    "sales_date": "ds",
                    "demand": "y",
                }
            )
        )
 
        dataframe["ds"] = pd.to_datetime(
            dataframe["ds"]
        )
 
        dataframe = dataframe.set_index("ds")
 
        # Extend the series through TODAY (not just the last actual
        # sale date) so the forecast's h-day horizon starts counting
        # from now, the same reference point for every product —
        # instead of silently continuing from whenever each product
        # last happened to sell.
        full_index = pd.date_range(
            start=dataframe.index.min(),
            end=pd.Timestamp(date.today()),
            freq="D",
        )
 
        dataframe = (
            dataframe
            .reindex(full_index, fill_value=0)
            .rename_axis("ds")
            .reset_index()
        )
 
        dataframe["unique_id"] = str(product_id)
 
        return dataframe[
            [
                "unique_id",
                "ds",
                "y",
            ]
        ]
 
 
    def _run_model(self, dataframe, horizon):
        model = StatsForecast(
            models=[
                AutoARIMA(),
            ],
            freq="D",
        )
 
        return model.forecast(
            df=dataframe,
            h=horizon,
            level=[90],
        )
 
 
    def _save_forecast(self, product_id, rows):
        (
            Forecast.objects
            .filter(
                product_id=product_id,
                model_name=MODEL_NAME,
            )
            .delete()
        )
 
        Forecast.objects.bulk_create(rows)
 
 
    def _to_forecast_rows(self, forecast_dataframe, product_id):
        lower_column = "AutoARIMA-lo-90"
        upper_column = "AutoARIMA-hi-90"
 
        rows = []
 
        for record in forecast_dataframe.to_dict("records"):
 
            prediction = max(
                float(record["AutoARIMA"]),
                0,
            )
 
            lower = max(
                float(
                    record.get(
                        lower_column,
                        prediction,
                    )
                ),
                0,
            )
 
            upper = max(
                float(
                    record.get(
                        upper_column,
                        prediction,
                    )
                ),
                0,
            )
 
            rows.append(
                Forecast(
                    product_id=product_id,
                    forecast_date=pd.to_datetime(
                        record["ds"]
                    ).date(),
                    predicted_quantity=prediction,
                    lower_bound=lower,
                    upper_bound=upper,
                    model_name=MODEL_NAME,
                )
            )
 
        return rows
 
 
    def history_for_display(self, product_id, days=90):
        history = list(
            SalesQuery.product_daily_history(product_id)
        )
 
        return (
            history[-days:]
            if days
            else history
        )
 