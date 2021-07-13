"""DiffSync model definitions for Grafana Dashboards."""
from typing import Optional
from diffsync import DiffSync, DiffSyncModel
from nautobot_plugin_chatops_grafana.models import Dashboard
from nautobot_plugin_chatops_grafana.grafana import handler


class DashboardModel(DiffSyncModel):
    """DashboardModel class used to model the stores response into a consumable format."""

    _modelname = "dashboard"
    _identifiers = ("slug",)
    _attributes = (
        "uid",
        "friendly_name",
    )

    slug: str
    uid: str
    friendly_name: Optional[str]

    @classmethod
    def create(cls, diffsync: DiffSync, ids: dict, attrs: dict) -> Optional[DiffSyncModel]:
        """Handler to create a Site object if it does not exist as per the diff.

        Args:
            diffsync (DiffSync): DiffSync
            ids (dict): Identifiers in the DiffSync model
            attrs (dict): Additional attributes in the DiffSync model

        Returns:
            Optional[DiffSyncModel]: [description]
        """
        item = super().create(ids=ids, diffsync=diffsync, attrs=attrs)
        Dashboard.objects.create(
            dashboard_slug=ids["slug"],
            dashboard_uid=attrs["uid"],
            friendly_name=attrs["friendly_name"],
        )
        return item

    def update(self, attrs: dict) -> Optional[DiffSyncModel]:
        """Update will handle updating elements we care about in the attrs on the site object.

        Args:
            attrs (dict): attributes that require an update in dcim.site

        Returns:
            Optional[DiffSyncModel]: Updated model.
        """
        dashboard_object = Dashboard.objects.get(dashboard_slug=self.slug)

        for key, value in attrs.items():
            setattr(dashboard_object, key, value)
        dashboard_object.save()
        return super().update(attrs)

    def delete(self) -> Optional[DiffSyncModel]:
        """Delete elements no longer needed on the Sites objects.

        NOTE: We are not handling deletes at this time due to the soft requirement of regions
        being referenced for automation purposes. If we need to track Regions from an external
        SoT outside of the stores API, then we can start handling it here.

        Returns:
            Optional[DiffSyncModel]: Updated model.
        """
        Dashboard.objects.get(dashboard_slug=self.slug).delete()

        super().delete()
        return self


class NautobotDashboard(DiffSync):
    """NautobotDashboard class used to represent the data model for nautobot_plugin_chatops_grafana.models.Dashboard."""

    dashboard = DashboardModel

    top_level = ["dashboard"]

    def __init__(self, *args, **kwargs):
        """Initialize the DiffSync model and populate the site."""
        super().__init__(*args, **kwargs)
        dashboards = Dashboard.objects.all()

        for dashboard in dashboards:
            # Create a site record for this item
            self.add(
                self.dashboard(
                    uid=dashboard.dashboard_uid, slug=dashboard.dashboard_slug, friendly_name=dashboard.friendly_name
                )
            )


class GrafanaDashboard(DiffSync):
    """QTSite class used to represent the data model from the QuikTrip Enterprise API."""

    dashboard = DashboardModel

    top_level = ["dashboard"]

    _required_fields = ("uid", "uri")

    def __init__(self, *args, **kwargs):
        """Initialize the Enterprise API stores DiffSync model and populate the object."""
        super().__init__(*args, **kwargs)
        dashboards = handler.get_dashboards()

        for dashboard in dashboards:
            # Validation to ensure the required keys exist. If not, fail and continue to the next.
            if not all(x in dashboard.keys() for x in self._required_fields):
                raise ValueError(f"Dashboard {dashboard} missing fields . Must have all of {self._required_fields}")

            # Create a site record for this item
            self.add(
                self.dashboard(
                    slug=dashboard["uri"].replace("db/", ""),
                    uid=dashboard["uid"],
                    friendly_name=dashboard.get("title", ""),
                )
            )
