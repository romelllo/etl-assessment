from tortoise import Tortoise, fields, models


class Business(models.Model):
    id = fields.IntField(pk=True)
    timezone = fields.CharField(max_length=50)
    rating = fields.FloatField()
    max_rating = fields.FloatField()
    review_count = fields.IntField()

    categories = fields.ReverseRelation["Category"]
    hours = fields.ReverseRelation["BusinessHours"]


class BusinessHours(models.Model):
    id = fields.IntField(pk=True)
    business = fields.ForeignKeyField("models.Business", related_name="hours")
    day = fields.CharField(max_length=10)
    shift1_start = fields.CharField(max_length=5, null=True)
    shift1_end = fields.CharField(max_length=5, null=True)
    shift2_start = fields.CharField(max_length=5, null=True)
    shift2_end = fields.CharField(max_length=5, null=True)


class Category(models.Model):
    id = fields.IntField(pk=True)
    business = fields.ForeignKeyField("models.Business", related_name="categories")
    category = fields.CharField(max_length=100)


# Registering the models
Tortoise.init_models(["__main__"], "models")
