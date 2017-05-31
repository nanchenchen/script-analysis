from django.core.management.base import BaseCommand, make_option, CommandError

class Command(BaseCommand):
    help = "Extract topics for a dataset."
    args = "<dataset id>"
    option_list = BaseCommand.option_list + (
        make_option('--topics',
                    dest='num_topics',
                    default=30,
                    help='The number of topics to model'),
        make_option('--name',
                    dest='name',
                    default='my topic model',
                    help="The name for your keyword dictionary"),
    )

    def handle(self, dataset_id, *args, **options):
        num_topics = options.get('num_topics')
        name = options.get('name')

        if not dataset_id:
            raise CommandError("Dataset id is required.")
        try:
            dataset_id = int(dataset_id)
        except ValueError:
            raise CommandError("Dataset id must be a number.")

        # from pyanalysis.apps.enhance.tasks import diff_topic_context, standard_topic_pipeline
        from pyanalysis.apps.enhance.tasks import diff_topic_context_with_merged, standard_topic_pipeline

        context = diff_topic_context_with_merged(name, dataset_id=dataset_id)
        standard_topic_pipeline(context, dataset_id=dataset_id, num_topics=int(num_topics))