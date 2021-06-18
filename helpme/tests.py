from io import StringIO

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.sites.models import Site
from django.urls import reverse
from django.core.management import call_command

from .models import Ticket, Comment, Team, Category, Question, StatusChoices, PriorityChoices, VisibilityChoices, CommentTypeChoices
from .settings import app_settings

class ModelTests(TestCase):

    def test_create_ticket_model(self):
        ticket = Ticket.objects.create(subject="Test", description="Test description", category=app_settings.TICKET_CATEGORIES.HELP)
        
        self.assertEqual(ticket.site.domain, "example.com")
        self.assertEqual(ticket.status, StatusChoices.OPEN)
        self.assertEqual(ticket.priority, PriorityChoices.MEDIUM)

        
    def test_create_comment_model(self):
        ticket = Ticket.objects.create(subject="Test", description="Test description", category=app_settings.TICKET_CATEGORIES.HELP)
        comment = Comment.objects.create(content="This is an example comment", ticket=ticket)
    
        self.assertEqual(comment.visibility, VisibilityChoices.REPORTERS)
        self.assertEqual(comment.comment_type, CommentTypeChoices.MESSAGE)

        
class ClientTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.support = get_user_model().objects.create(username="supportuser")
        cls.student = get_user_model().objects.create(username="testuser")
        cls.admin = get_user_model().objects.create_superuser(username="admin")
        
        support = Permission.objects.get(codename="see_support_tickets")
        view_team = Permission.objects.get(codename="view_team")
        view_category = Permission.objects.get(codename="view_category")
        view_question = Permission.objects.get(codename="view_question")
        add_category = Permission.objects.get(codename="add_category")
        add_question = Permission.objects.get(codename="add_question")
        cls.support.user_permissions.add(support, view_team, add_category, add_question, view_category, view_question)
        
        cls.support_team = Team.objects.create(name="Support", global_team=False, categories=str(app_settings.TICKET_CATEGORIES.HELP))
        site = Site.objects.get(pk=1)
        cls.support_team.sites.add(site)
        cls.support_team.members.add(cls.support)

        cls.basic_category = Category.objects.create(category="Testing")
        cls.basic_category.category_sites.add(site)
        cls.question = Question.objects.create(question="What is 2 + 2?", answer="4", category=cls.basic_category)

        
    def setUp(self):
        self.simple_ticket = Ticket.objects.create(subject="ABC", description="123", category=app_settings.TICKET_CATEGORIES.COMMENT, user=self.student)
        self.simple_ticket.teams.add(self.support_team)
        self.client.force_login(self.support)

        
    def test_create_ticket(self):
        uri = reverse("helpme-api-create-ticket")
        self.assertEqual(Ticket.objects.all().count(), 1)
        
        response = self.client.post(uri, {"subject": "Test subject", "description": "Test description", "category": app_settings.TICKET_CATEGORIES.HELP}, follow=True)
        self.assertEqual(Ticket.objects.all().count(), 2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [(reverse("helpme_admin:dashboard"), 302)])
        ticket = Ticket.objects.get(subject="Test subject")
        self.assertEqual(ticket.user, self.support)
        self.assertQuerysetEqual(ticket.teams.all(), ['<Team: Support>'])
        self.assertEqual(ticket.user_meta, {'os': {'family': 'other', 'version': ''}, 'device': 'other', 'browser': {'family': 'other', 'version': ''}, 'ip_address': '127.0.0.1', 'mobile_tablet_or_pc': 'unknown'})


    def test_create_anonymous_ticket(self):
        uri = reverse("helpme:anonymous")
        self.assertEqual(Ticket.objects.all().count(), 1)
        
        response = self.client.post(uri, {"description": "Hello world", "full_name": "Test User", "email": "test@test.com"}, follow=True)
        self.assertEqual(Ticket.objects.all().count(), 2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [(reverse("helpme:anonymous"), 302)])
        ticket = Ticket.objects.get(subject="Contact Us")
        self.assertEqual(ticket.description, "Hello world")
        self.assertDictEqual(ticket.user_meta, {'os': {'family': 'other', 'version': ''}, 'device': 'other', 'browser': {'family': 'other', 'version': ''}, 'ip_address': '127.0.0.1', 'mobile_tablet_or_pc': 'unknown', 'full_name': 'Test User', 'email': 'test@test.com', 'phone_number': ''})

        
    def test_dashboard_support(self):
        uri = reverse("helpme_admin:dashboard")
        response = self.client.get(uri)
        self.assertEqual(self.support.has_perm("helpme.see_support_tickets"), True)
        self.assertContains(response, reverse("helpme_admin:ticket-detail", args=[self.simple_ticket.uuid]))
        self.assertContains(response, 'testuser - ABC')
        self.assertContains(response, "Status:")
        self.assertContains(response, "Open")


    def test_dashboard_student(self):
        self.client.force_login(self.student)
        uri = reverse("helpme:dashboard")
        response = self.client.get(uri)
        self.assertEqual(self.student.has_perm("helpme.see_support_tickets"), False)
        self.assertContains(response, 'ABC')
        self.assertContains(response, "Status: ")
        self.assertContains(response, "Open")


    def test_dashboard_filter_by_site(self):
        self.client.force_login(self.student)
        site = Site.objects.create(domain="site2.com", name="Site 2")
        Ticket.objects.create(subject="Other site", description="Other site description", user=self.student, category=app_settings.TICKET_CATEGORIES.HELP, site=site)
        uri = reverse("helpme:dashboard")
        response = self.client.get(uri)

        self.assertContains(response, "ABC")
        self.assertNotContains(response, "Other site")


    def test_dashboard_superuser(self):
        """
        Superuser should be able to see all tickets, including on other sites
        """
        
        self.client.force_login(self.admin)

        site = Site.objects.create(domain="site2.com", name="Site 2")
        Ticket.objects.create(subject="Other site", description="Other site description", user=self.support, category=app_settings.TICKET_CATEGORIES.HELP, site=site)
        uri = reverse("helpme_admin:dashboard")
        response = self.client.get(uri)

        self.assertContains(response, "testuser - ABC")
        self.assertContains(response, "supportuser - Other site")


    def test_dashboard_filter_by_status(self):
        active_ticket = Ticket.objects.create(subject="Active ticket", description="Test filter", category=app_settings.TICKET_CATEGORIES.HELP, status=StatusChoices.ACTIVE, user=self.support)
        active_ticket.teams.add(self.support_team)
        
        # filter by active tickets
        uri = reverse("helpme_admin:dashboard")
        response = self.client.get(uri, {'s': '10'})

        self.assertContains(response, 'supportuser - Active ticket')
        self.assertNotContains(response, 'testuser - ABC')

        # filter by active and open tickets
        new_response = self.client.get(uri, {"s": "1,10"})
        self.assertContains(new_response, 'supportuser - Active ticket')
        self.assertContains(new_response, 'testuser - ABC')

        
    def test_ticket_detail_support(self):
        uri = reverse("helpme_admin:ticket-detail", args=[self.simple_ticket.uuid])
        response = self.client.get(uri)

        # ticket information and update form
        self.assertContains(response, "ABC")
        self.assertContains(response, "123")
        self.assertContains(response, '<select name="status"')
        self.assertContains(response, '<option value="3" selected>Medium</option>')
        self.assertContains(response, '<option value="1" selected>Comment</option>')
        self.assertContains(response, 'name="teams"')
        self.assertContains(response, '<select name="assigned_to"')
        self.assertContains(response, '<input type="text" name="dev_ticket"')
        self.assertContains(response, "Reporter:")
        self.assertContains(response, "Reporter Meta")
        self.assertContains(response, "Site:")
        self.assertContains(response, "Created:")
        self.assertContains(response, "Last Updated:")
        self.assertContains(response, '<input type="submit" value="Update"')

        # comment form
        self.assertContains(response, '<textarea name="content"')
        self.assertContains(response, '<select name="visibility"')
        self.assertContains(response, '<input type="submit" value="Reply"')


    def test_ticket_detail_student(self):
        self.client.force_login(self.student)
        uri = reverse("helpme_admin:ticket-detail", args=[self.simple_ticket.uuid])
        response = self.client.get(uri)

        self.assertEqual(response.status_code, 403)

        
    def test_ticket_detail_update(self):
        uri = reverse("helpme_admin:ticket-detail", args=[self.simple_ticket.uuid])
        response = self.client.post(uri, {"status": StatusChoices.ACTIVE, "category": app_settings.TICKET_CATEGORIES.COMMENT, "priority": PriorityChoices.MEDIUM}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [(reverse("helpme_admin:ticket-detail", args=[self.simple_ticket.uuid]), 302)])
        self.assertContains(response, '<option value="10" selected>Active</option>')
        self.simple_ticket.refresh_from_db()
        self.assertEqual(self.simple_ticket.status, StatusChoices.ACTIVE)
        self.assertEqual(self.simple_ticket.comments.all().count(), 1)
        event = self.simple_ticket.comments.get(comment_type=CommentTypeChoices.EVENT)
        self.assertEqual(event.user, self.support)

        
    def test_comment_creation(self):
        self.assertEqual(Comment.objects.all().count(), 0)
        uri = reverse("helpme-api-create-comment", args=[self.simple_ticket.uuid])
        response = self.client.post(uri, {"content": "This is a test comment", "visibility": VisibilityChoices.REPORTERS}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [(reverse("helpme_admin:ticket-detail", args=[self.simple_ticket.uuid]), 302)])
        
        self.assertContains(response, "This is a test comment")
        self.assertEqual(Comment.objects.all().count(), 1)

        self.simple_ticket.refresh_from_db()
        self.assertEqual(self.simple_ticket.comments.all().count(), 1)


    def test_teams_view_support(self):
        uri = reverse("helpme_admin:team-list")
        response = self.client.get(uri)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Teams")
        self.assertContains(response, reverse("helpme_admin:team-detail", args=[self.support_team.uuid]))
        self.assertContains(response, '> Support </a>')


    def test_teams_view_admin(self):
        self.client.force_login(self.admin)
        uri = reverse("helpme_admin:team-list")
        response = self.client.get(uri)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Manage Teams")
        self.assertContains(response, reverse("helpme_admin:team-detail", args=[self.support_team.uuid]))
        self.assertContains(response, '> Support </a>')


    def test_teams_view_student(self):
        self.client.force_login(self.student)
        uri = reverse("helpme_admin:team-list")
        response = self.client.get(uri)

        # regular user should not have permission to view this page
        self.assertEqual(response.status_code, 403)


    def test_team_detail_support(self):
        uri = reverse("helpme_admin:team-detail", args=[self.support_team.uuid])
        response = self.client.get(uri)

        # lists team details but cannot update them 
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Support")
        self.assertContains(response, "Site(s):")
        self.assertContains(response, "example.com")
        self.assertContains(response, "Handles Categories:")
        self.assertContains(response, "Help")
        self.assertContains(response, "Members:")
        self.assertContains(response, "supportuser")
        self.assertNotContains(response, '<input type="submit" value="Update"')


    def test_team_detail_admin(self):
        self.client.force_login(self.admin)
        uri = reverse("helpme_admin:team-detail", args=[self.support_team.uuid])
        response = self.client.get(uri)

        # form to update team details
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<input type="text" name="name"')
        self.assertContains(response, 'name="categories"')
        self.assertContains(response, 'name="members"')
        self.assertContains(response, '<input type="submit" value="Update"')
        

    def test_team_detail_student(self):
        self.client.force_login(self.student)
        uri = reverse("helpme_admin:team-detail", args=[self.support_team.uuid])
        response = self.client.get(uri)

        # regular user should not have permission to view this page
        self.assertEqual(response.status_code, 403)


    def test_faq_view(self):
        uri = reverse("helpme:faq")
        response = self.client.get(uri)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Testing")
        self.assertContains(response, "What is 2 + 2?")
        self.assertContains(response, "4")


    def test_category_creation(self):
        uri = reverse("helpme-api-create-category")
        response = self.client.post(uri, {"category": "New!"}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [(reverse("helpme_admin:faq-create"), 302)])
        self.assertContains(response, "New!")


    def test_question_creation(self):
        uri = reverse("helpme-api-create-question")
        response = self.client.post(uri, {"question": "What color is the sky?", "answer": "Blue", "category": self.basic_category.pk}, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [(reverse("helpme_admin:faq-create"), 302)])
        self.assertContains(response, "What color is the sky?")
        self.assertContains(response, "Blue")


class ModuleTests(TestCase):
    '''
    Tests to make sure basic elements are not missing from the package
    '''
    def test_for_missing_migrations(self):
        output = StringIO()

        try:
            call_command('makemigrations', interactive=False, dry_run=True, check=True, stdout=output)

        except SystemExit as e:
            # The exit code will be 1 when there are no missing migrations
            try:
                assert e == '1'
            except:
                self.fail("\n\nHey, There are missing migrations!\n\n %s" % output.getvalue())
