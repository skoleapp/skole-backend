from django.core.validators import MinValueValidator
from django.db import models



class BetaCode(models.Model):
    code = models.CharField(max_length=8, unique=True)
    usages = models.IntegerField(validators=[MinValueValidator(1)])

    def __str__(self) -> str:
        return f"{self.code} - Usages left: {self.usages}"

    def decrement_usages(self) -> "BetaCode":
        self.usages -= 1

        if self.usages == 0:
            self.delete()
        else:
            self.save()

        return self
