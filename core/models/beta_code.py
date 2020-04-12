from django.core.validators import MinValueValidator
from django.db import models


class BetaCodeManager(models.Manager["BetaCode"]):
    def decrement_usages(self, code: "BetaCode") -> "BetaCode":
        code.usages -= 1

        if code.usages == 0:
            code.delete()
        else:
            code.save()

        return code


class BetaCode(models.Model):
    code = models.CharField(max_length=8, unique=True)
    usages = models.IntegerField(validators=[MinValueValidator(1)])

    objects = BetaCodeManager()

    def __str__(self) -> str:
        return f"{self.code} - Usages left: {self.usages}"
