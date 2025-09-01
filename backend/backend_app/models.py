from django.db import models

class Cursus(models.Model):
    # ... (code zoals je die al hebt)
    cursus = models.CharField(max_length=200, blank=True, null=True)
    cursusdatum = models.DateField(blank=True, null=True)
    refresher = models.BooleanField(default=False)
    geldigheid_jaren = models.CharField(max_length=50, blank=True, null=True)
    geldigheid_datum = models.DateField(blank=True, null=True)
    reminder_sent = models.BooleanField(default=False)
    deelnemers = models.ManyToManyField(
        'Deelnemer',
        related_name='cursussen',
        blank=True
    )

    class Meta:
        verbose_name_plural = "Cursussen"
    def __str__(self):
        return f"{self.cursus} op {self.cursusdatum}"

class Deelnemer(models.Model):
    aanhef = models.CharField(max_length=5, blank=True, null=True)
    voornaam = models.CharField(max_length=100, blank=True, null=True)
    tussenvoegsel = models.CharField(max_length=50, blank=True, null=True)
    achternaam = models.CharField(max_length=100, blank=True, null=True)
    bedrijfsnaam = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    geboortedatum = models.DateField(blank=True, null=True)
    telefoonnummer = models.CharField(max_length=20, blank=True, null=True)
    windaId = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Deelnemers"
        constraints = [
            models.UniqueConstraint(
                fields=['voornaam', 'tussenvoegsel', 'achternaam', 'geboortedatum'],
                name='unieke_deelnemer_constraint'
            )
        ]

    def __str__(self):
        # Definitieve aanpassing:
        name_parts = [self.voornaam, self.tussenvoegsel, self.achternaam]
        full_name = " ".join(filter(None, name_parts))
        return full_name
    
class QREvent(models.Model):
    titel = models.CharField(max_length=200, blank=True, null=True)
    datum = models.DateField(blank=True, null=True)
    locatie = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.titel or 'Onbekend event'

# Nieuw model voor QR-deelnemers
class QRDeelnemer(models.Model):
    voornaam = models.CharField(max_length=100)
    achternaam = models.CharField(max_length=100)
    email = models.EmailField()
    telefoonnummer = models.CharField(max_length=20, blank=True, null=True)
    
    # ForeignKey om de deelnemer aan een specifiek event te koppelen
    qr_event = models.ForeignKey(QREvent, on_delete=models.CASCADE, related_name='deelnemers')

    def __str__(self):
        return f"{self.voornaam} {self.achternaam}"