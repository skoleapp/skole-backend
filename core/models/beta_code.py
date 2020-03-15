from django.db import models


class BetaCodeManager(models.Manager):  # type: ignore[type-arg]
    def decrement_usages(self, code: "BetaCode") -> "BetaCode":
        code.usages -= 1
        code.save()
        return code


class BetaCode(models.Model):
    code = models.CharField(max_length=8, unique=True)
    usages = models.IntegerField()

    objects = BetaCodeManager()
