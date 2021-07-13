"""API views for grafana backend services."""
from django.http import JsonResponse
from django.views import View

from diffsync import DiffSyncFlags
from nautobot_plugin_chatops_grafana.diffsync.models import NautobotDashboard, GrafanaDashboard
from nautobot_plugin_chatops_grafana.grafana import handler


class GrafanaDashboards(View):
    """Fetch Grafana Dashboard list from the grafana API."""

    http_method_names = ["get", "put"]

    def put(self, request, *args, **kwargs):
        """Handle an inbount PUT request."""
        df_flags = DiffSyncFlags.NONE if request.POST.get("delete") else DiffSyncFlags.SKIP_UNMATCHED_DST

        # Load the stores info retrieved from the API into the DiffSync model.
        diff_nautobot_dashboards = NautobotDashboard()

        # Load the Sites object retrieved from the nautobot DB into the DiffSync model.
        diff_grafana_dashboards = GrafanaDashboard()

        diff_site = diff_nautobot_dashboards.diff_from(diff_grafana_dashboards, flags=df_flags)
        if not diff_site.has_diffs():
            return JsonResponse(data={"data": "No diffs found for dashboards."})

        diff_nautobot_dashboards.sync_from(diff_grafana_dashboards, flags=df_flags)
        return JsonResponse(data={"data": diff_site.str()})

    def get(self, request, *args, **kwargs):
        """Handle an inbount GET request."""
        data = handler.get_dashboards()
        return JsonResponse(data={"data": data})
