# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-29 21:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='AuthorAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=255)),
                ('value', models.CharField(max_length=511)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='noveltorpedo.Author')),
            ],
            options={
                'db_table': 'noveltorpedo_author_attributes',
            },
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=511)),
                ('spider', models.CharField(max_length=255)),
                ('wait', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('authors', models.ManyToManyField(to='noveltorpedo.Author')),
            ],
        ),
        migrations.CreateModel(
            name='StoryAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=255)),
                ('value', models.CharField(max_length=511)),
                ('story', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='noveltorpedo.Story')),
            ],
            options={
                'db_table': 'noveltorpedo_story_attributes',
            },
        ),
        migrations.CreateModel(
            name='StoryHost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=511)),
                ('last_scraped', models.DateTimeField()),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='noveltorpedo.Host')),
                ('story', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='noveltorpedo.Story')),
            ],
            options={
                'db_table': 'noveltorpedo_story_hosts',
            },
        ),
        migrations.CreateModel(
            name='StorySegment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(max_length=511)),
                ('contents', models.TextField(default='')),
                ('published', models.DateTimeField()),
                ('story', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='noveltorpedo.Story')),
            ],
            options={
                'db_table': 'noveltorpedo_story_segments',
            },
        ),
        migrations.AddField(
            model_name='story',
            name='hosts',
            field=models.ManyToManyField(through='noveltorpedo.StoryHost', to='noveltorpedo.Host'),
        ),
    ]
