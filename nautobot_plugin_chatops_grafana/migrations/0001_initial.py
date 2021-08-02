# Generated by Django 3.1.13 on 2021-07-30 14:42

import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("extras", "0005_configcontext_device_types"),
    ]

    operations = [
        migrations.CreateModel(
            name="Dashboard",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("dashboard_slug", models.CharField(max_length=255, unique=True)),
                ("friendly_name", models.CharField(blank=True, default="", max_length=255)),
                ("dashboard_uid", models.CharField(max_length=64, unique=True)),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "ordering": ["dashboard_slug"],
            },
        ),
        migrations.CreateModel(
            name="Panel",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("command_name", models.CharField(max_length=64)),
                ("friendly_name", models.CharField(default="", max_length=64)),
                ("panel_id", models.IntegerField()),
                ("active", models.BooleanField(default=False)),
                (
                    "dashboard",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="nautobot_plugin_chatops_grafana.dashboard"
                    ),
                ),
            ],
            options={
                "ordering": ["command_name", "dashboard"],
            },
        ),
        migrations.CreateModel(
            name="PanelVariable",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("name", models.CharField(max_length=32)),
                ("friendly_name", models.CharField(max_length=64)),
                ("query", models.CharField(max_length=64)),
                ("includeincmd", models.BooleanField(default=False)),
                ("includeinurl", models.BooleanField(default=True)),
                ("modelattr", models.CharField(max_length=64)),
                ("value", models.TextField(max_length=64)),
                ("response", models.CharField(max_length=255)),
                (
                    "filter",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("positional_order", models.IntegerField(default=100)),
                (
                    "panel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="nautobot_plugin_chatops_grafana.panel"
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
    ]
