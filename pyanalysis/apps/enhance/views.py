from django.shortcuts import render
from django.views.generic import ListView, DetailView

import models

# Create your views here.
class TopicModelIndexView(ListView):
    context_object_name = 'topic_models'
    queryset = models.TopicModel.objects.all()
    template_name = 'topic_browser/models.html'


class TopicModelDetailView(DetailView):
    pk_url_kwarg = 'model_id'
    context_object_name = 'topic_model'
    model = models.TopicModel
    template_name = 'topic_browser/model_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TopicModelDetailView, self).get_context_data(**kwargs)

        # Add in a QuerySet of tokens for each topic
        tokens_for_topics = {}
        max_tokens = 0
        topics = context['topic_model'].topics.all().prefetch_related('tokens')
        for topic in topics:
            tokens = list(topic.token_scores.order_by('-probability').prefetch_related('token'))
            tokens_for_topics[topic.id] = tokens
            max_tokens = max(max_tokens, len(tokens))

        # transpose the token lists
        token_rows = []
        for token_i in range(max_tokens):
            row = []

            for topic in topics:
                tokens = tokens_for_topics[topic.id]
                if token_i < len(tokens):
                    row.append(tokens[token_i])
                else:
                    row.append(None)

            token_rows.append(row)

        context['token_rows'] = token_rows

        return context


class TopicDetailView(DetailView):
    pk_url_kwarg = 'topic_id'
    context_object_name = 'topic'
    model = models.Topic
    template_name = 'topic_browser/topic_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TopicDetailView, self).get_context_data(**kwargs)
        TopicDetailView.get_topic_data(context, topic=self.object)
        return context

    @classmethod
    def get_topic_data(cls, context, topic, token=None):
        topic_model = topic.model
        context['topic'] = topic
        context['token'] = token
        context['topic_model'] = topic_model
        context['topic_tokens'] = topic.token_scores.all()

        #Dumb
        topicvector_class = models.ScriptTopic


        examples = topicvector_class.get_examples(topic=topic)
        if token:
            examples = examples.filter(script__tokens__text=token)

        context['examples'] = examples[:100].prefetch_related('script')




class TopicDictTokenDetailView(DetailView):
    pk_url_kwarg = 'token_id'
    context_object_name = 'token'
    model = models.TopicDictToken
    template_name = 'topic_browser/topic_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TopicDictTokenDetailView, self).get_context_data(**kwargs)
        topictoken = self.object
        TopicDetailView.get_topic_data(context, topic=self.object.topic, token=topictoken.token.text)
        return context
