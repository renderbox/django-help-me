# --------------------------------------------
# Copyright 2019, Grant Viklund
# @Author: Grant Viklund
# @Date:   2019-08-06 15:10:20
# --------------------------------------------

from rest_framework import serializers

from helpme.models import Ticket, Comment, Category, Question


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('category', 'subject', 'description')
        

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('content', 'visibility')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('category', 'category_sites', 'global_category', 'category_excluded_sites')


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('question', 'answer', 'category', 'sites', 'global_question', 'excluded_sites')
