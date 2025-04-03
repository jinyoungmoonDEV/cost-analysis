from mongoengine import *

from spaceone.core.model.mongo_model import MongoModel


class BudgetUsage(MongoModel):
    budget_id = StringField(max_length=40, required=True)
    name = StringField(max_length=255, default="")
    date = StringField(max_length=7, required=True)
    cost = FloatField(required=True)
    limit = FloatField(required=True)
    currency = StringField(default=None, null=True)
    budget = ReferenceField("Budget", reverse_delete_rule=CASCADE)
    resource_group = StringField(max_length=40, choices=["WORKSPACE", "PROJECT"])
    project_id = StringField(max_length=40, default=None, null=True)
    data_source_id = StringField(max_length=40)
    workspace_id = StringField(max_length=40, default=None, null=True)
    domain_id = StringField(max_length=40)
    updated_at = DateTimeField(auto_now=True)

    meta = {
        "updatable_fields": ["name", "cost", "limit"],
        "minimal_fields": ["budget_id", "name", "date", "cost", "limit"],
        "change_query_keys": {"user_projects": "project_id"},
        "ordering": ["budget_id", "date"],
        "indexes": [
            "budget_id",
            "name",
            "date",
            "resource_group",
            "project_id",
            "workspace_id",
            "domain_id",
        ],
    }
