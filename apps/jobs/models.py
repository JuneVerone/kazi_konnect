import uuid
from django.db import models
from django.core.exceptions import ValidationError
from apps.users.models import CustomUser


class Job(models.Model):

    class Status(models.TextChoices):
        OPEN        = 'OPEN',        'Open'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED   = 'COMPLETED',   'Completed'
        CANCELLED   = 'CANCELLED',   'Cancelled'

    class Category(models.TextChoices):
        DESIGN         = 'DESIGN',         'Design'
        DEVELOPMENT    = 'DEVELOPMENT',    'Development'
        WRITING        = 'WRITING',        'Writing'
        MARKETING      = 'MARKETING',      'Marketing'
        VIDEO          = 'VIDEO',          'Video & Animation'
        DATA           = 'DATA',           'Data & Analytics'
        ADMIN          = 'ADMIN',          'Admin & Virtual Assistant'
        OTHER          = 'OTHER',          'Other'

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client      = models.ForeignKey(
                    CustomUser,
                    on_delete=models.CASCADE,
                    related_name='posted_jobs',
                    limit_choices_to={'role': CustomUser.Role.CLIENT},
                  )
    awarded_to  = models.ForeignKey(
                    CustomUser,
                    on_delete=models.SET_NULL,
                    related_name='awarded_jobs',
                    null=True,
                    blank=True,
                    limit_choices_to={'role': CustomUser.Role.FREELANCER},
                  )
    title       = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    budget      = models.DecimalField(max_digits=10, decimal_places=2)
    category    = models.CharField(max_length=50, choices=Category.choices, db_index=True)
    status      = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True)
    deadline    = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Job'
        verbose_name_plural = 'Jobs'
        ordering            = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.status})'

    def clean(self):
        if self.awarded_to and self.status == self.Status.OPEN:
            raise ValidationError('A job cannot be OPEN and have an awarded freelancer.')

    @property
    def is_open(self):
        return self.status == self.Status.OPEN

    @property
    def proposal_count(self):
        return self.proposals.count()


class Proposal(models.Model):

    class Status(models.TextChoices):
        PENDING   = 'PENDING',   'Pending'
        ACCEPTED  = 'ACCEPTED',  'Accepted'
        REJECTED  = 'REJECTED',  'Rejected'
        WITHDRAWN = 'WITHDRAWN', 'Withdrawn'

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job          = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='proposals')
    freelancer   = models.ForeignKey(
                     CustomUser,
                     on_delete=models.CASCADE,
                     related_name='submitted_proposals',
                     limit_choices_to={'role': CustomUser.Role.FREELANCER},
                   )
    bid_amount   = models.DecimalField(max_digits=10, decimal_places=2)
    cover_letter = models.TextField()
    status       = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Proposal'
        verbose_name_plural = 'Proposals'
        ordering            = ['-created_at']
        constraints         = [
            models.UniqueConstraint(
                fields=['job', 'freelancer'],
                name='unique_proposal_per_job'
            )
        ]

    def __str__(self):
        return f'{self.freelancer.full_name} → {self.job.title}'