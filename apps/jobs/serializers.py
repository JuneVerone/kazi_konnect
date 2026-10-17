from rest_framework import serializers
from .models import Job, Proposal
from apps.users.serializers import UserProfileSerializer


class ProposalSerializer(serializers.ModelSerializer):
    freelancer = UserProfileSerializer(read_only=True)

    class Meta:
        model  = Proposal
        fields = [
            'id', 'job', 'freelancer', 'bid_amount',
            'cover_letter', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'freelancer', 'status', 'created_at', 'updated_at']


class ProposalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Proposal
        fields = ['id', 'job', 'bid_amount', 'cover_letter']
        read_only_fields = ['id']

    def validate_job(self, value):
        if not value.is_open:
            raise serializers.ValidationError(
                'You can only submit proposals for open jobs.'
            )
        return value

    def validate(self, attrs):
        request  = self.context['request']
        job      = attrs['job']
        freelancer = request.user

        if Proposal.objects.filter(job=job, freelancer=freelancer).exists():
            raise serializers.ValidationError(
                'You have already submitted a proposal for this job.'
            )
        return attrs

    def create(self, validated_data):
        validated_data['freelancer'] = self.context['request'].user
        return super().create(validated_data)


class JobListSerializer(serializers.ModelSerializer):
    client         = serializers.StringRelatedField(read_only=True)
    proposal_count = serializers.SerializerMethodField()

    class Meta:
        model  = Job
        fields = [
            'id', 'title', 'category', 'budget',
            'status', 'client', 'proposal_count', 'created_at',
        ]

    def get_proposal_count(self, obj):
        return obj.proposals.count()


class JobDetailSerializer(serializers.ModelSerializer):
    client     = UserProfileSerializer(read_only=True)
    awarded_to = UserProfileSerializer(read_only=True)
    proposals  = ProposalSerializer(many=True, read_only=True)

    class Meta:
        model  = Job
        fields = [
            'id', 'title', 'description', 'category', 'budget',
            'status', 'client', 'awarded_to', 'proposals',
            'deadline', 'created_at', 'updated_at',
        ]


class JobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Job
        fields = [
            'id', 'title', 'description',
            'category', 'budget', 'deadline',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['client'] = self.context['request'].user
        return super().create(validated_data)


class JobStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Job
        fields = ['status', 'awarded_to']

    def validate(self, attrs):
        status     = attrs.get('status', self.instance.status)
        awarded_to = attrs.get('awarded_to', self.instance.awarded_to)

        if status == Job.Status.IN_PROGRESS and not awarded_to:
            raise serializers.ValidationError(
                'You must award the job to a freelancer before marking it in progress.'
            )
        if status == Job.Status.OPEN and awarded_to:
            raise serializers.ValidationError(
                'Cannot set status to OPEN when a freelancer is already awarded.'
            )
        return attrs