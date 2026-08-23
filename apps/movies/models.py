"""Movie database models belong here when real MovieLens/TMDB data is integrated.

Week 1 deliberately uses service-layer demo data so migrations are not required
for the frontend foundation.
"""
from django.conf import settings
from django.db import models

class WebsiteRating(models.Model):
    """
    Stores one persistent movie rating for each real RMRS website user.

    Synthetic attack users are not stored here.
    """

    RATING_CHOICES = [
        (1, "1 star"),
        (2, "2 stars"),
        (3, "3 stars"),
        (4, "4 stars"),
        (5, "5 stars"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="website_ratings",
    )

    movie_id = models.PositiveIntegerField()

    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES
    )

    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-timestamp"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "movie_id"],
                name="unique_website_rating_per_user_movie",
            )
        ]

    def __str__(self):
        return f"{self.user} - Movie {self.movie_id}: {self.rating}/5"