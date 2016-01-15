# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-15 18:14
from __future__ import unicode_literals

import django.db.models.deletion
import django.utils.timezone
import yunity.base.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('name', yunity.base.models.MaxLengthCharField(max_length=255)),
                ('description', models.TextField(null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, yunity.base.models.HubbedMixin),
        ),
        migrations.CreateModel(
            name='Hub',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('target_id', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='HubMembership',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('hub', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Hub')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('description', models.TextField()),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('name', yunity.base.models.MaxLengthCharField(max_length=255, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('name', yunity.base.models.MaxLengthCharField(max_length=255, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, yunity.base.models.HubbedMixin),
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('name', yunity.base.models.MaxLengthCharField(max_length=255, null=True)),
                ('permissions', models.ManyToManyField(to='base.Permission')),
                ('team_hub', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Hub')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, yunity.base.models.HubbedMixin),
        ),
        migrations.AddField(
            model_name='hub',
            name='members',
            field=models.ManyToManyField(through='base.HubMembership', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='hub',
            name='target_content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='group',
            name='items',
            field=models.ManyToManyField(to='base.Item'),
        ),
        migrations.AlterUniqueTogether(
            name='hub',
            unique_together=set([('target_content_type', 'target_id')]),
        ),
    ]