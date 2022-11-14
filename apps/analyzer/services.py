from datetime import datetime

from apps.accounts.models import Activity
from apps.utils.constants import ACTIVITY_CATEGORIES


def get_categories_coverage(start_date, end_date):
    """
    This method returns how much of each category was created in the given period
    """
    keys = {
        category[0]: {"previous": 0, "current": 0} for category in ACTIVITY_CATEGORIES
    }
    time_range = end_date - start_date
    activities = Activity.objects.filter(
        start_date__gte=start_date - time_range, end_date__lte=end_date
    )
    current_period = activities.filter(start_date__gte=start_date)
    previous_period = activities.filter(end_date__lte=start_date)
    current_activities_count = current_period.count()
    result = []
    for activity in current_period:
        keys[activity.category]["current"] += 1
    for activity in previous_period:
        keys[activity.category]["previous"] += 1
    for category in keys.items():
        current_coverage = round(
            category[1]["current"] / current_activities_count * 100, 2
        )
        current_results = category[1]["current"]
        previous_results = category[1]["previous"] or 1
        variation = round(
            (current_results - previous_results) / previous_results * 100, 2
        )
        result.append(
            {
                "id": category[0],
                "name": [x[1] for x in ACTIVITY_CATEGORIES if x[0] == category[0]][0],
                "current_results": current_results,
                "previous_results": previous_results,
                "coverage": current_coverage,
                "variation": variation,
            }
        )
    result.sort(key=lambda x: x["coverage"], reverse=True)
    response = {"total": current_activities_count, "data": result}
    return response
