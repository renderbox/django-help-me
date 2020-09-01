# --------------------------------------------
# Copyright 2019, Grant Viklund
# @Author: Grant Viklund
# @Date:   2019-08-06 15:10:20
# --------------------------------------------

from rest_framework import serializers

from helpme.models import Comment, Category, Question


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('content', 'visibility')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('category', 'sites')


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('question', 'answer', 'category', 'sites')
