from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.sites.models import Site
from django.urls import reverse

from .models import Ticket, Comment, Team, StatusChoices, PriorityChoices, VisibilityChoices
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

        
class ClientTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.support = get_user_model().objects.create(username="supportuser")
        cls.student = get_user_model().objects.create(username="testuser")
        cls.admin = get_user_model().objects.create_superuser(username="admin")
        support = Permission.objects.get(codename="see-support-tickets")
        view_team = Permission.objects.get(codename="view_team")
        cls.support.user_permissions.add(support, view_team)
        
        cls.support_team = Team.objects.create(name="Support", global_team=False, categories=str(app_settings.TICKET_CATEGORIES.HELP))
        cls.support_team.sites.add(Site.objects.get(pk=1))
        cls.support_team.members.add(cls.support)

        
    def setUp(self):
        self.simple_ticket = Ticket.objects.create(subject="ABC", description="123", category=app_settings.TICKET_CATEGORIES.COMMENT, user=self.student)
        self.simple_ticket.teams.add(self.support_team)
        self.client.force_login(self.support)

        
    def test_support_request_view(self):
        uri = reverse("helpme:submit-request")
        self.assertEqual(Ticket.objects.all().count(), 1)
        
        response = self.client.post(uri, {"subject": "Test subject", "description": "Test description", "category": app_settings.TICKET_CATEGORIES.HELP}, follow=True)
        self.assertEqual(Ticket.objects.all().count(), 2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [(reverse("helpme:dashboard"), 302)])
        ticket = Ticket.objects.get(subject="Test subject")
        self.assertEqual(ticket.user, self.support)
        self.assertQuerysetEqual(ticket.teams.all(), ['<Team: Support>'])
        self.assertEqual(ticket.user_meta, {'device': 'Other', 'browser': 'Other ', 'IP address': '127.0.0.1', 'mobile/tablet/pc': 'Unknown', 'operating system': 'Other '})
        self.assertEqual(ticket.history[0]["event"], "created")
        self.assertEqual(ticket.history[0]["user"], 1)
        self.assertEqual(ticket.history[0]["username"], "supportuser")

        
    def test_dashboard_support(self):
        uri = reverse("helpme:dashboard")
        response = self.client.get(uri)
        self.assertEqual(self.support.has_perm("helpme.see-support-tickets"), True)
        self.assertContains(response, '<a href="/support/ticket/')
        self.assertContains(response, '>testuser - ABC</a>')
        self.assertContains(response, "Status: ")
        self.assertContains(response, "Open")
        self.assertContains(response, "Priority: ")
        self.assertContains(response, "Medium")


    def test_dashboard_student(self):
        self.client.force_login(self.student)
        uri = reverse("helpme:dashboard")
        response = self.client.get(uri)
        self.assertEqual(self.student.has_perm("helpme.see-support-tickets"), False)
        self.assertContains(response, '<a href="/support/ticket/')
        self.assertContains(response, '>testuser - ABC</a>')
        self.assertContains(response, "Status: ")
        self.assertContains(response, "Open")
        self.assertNotContains(response, "Priority: ")
        self.assertNotContains(response, "Medium")

        
    def test_ticket_detail_support(self):
        uri = reverse("helpme:ticket-detail", args=[self.simple_ticket.uuid])
        response = self.client.get(uri)

        # ticket information and update form
        self.assertContains(response, "ABC")
        self.assertContains(response, "123")
        self.assertContains(response, '<select name="status"')
        self.assertContains(response, '<option value="3" selected>Medium</option>')
        self.assertContains(response, '<option value="1" selected>Comment</option>')
        self.assertContains(response, '<option value="1" selected>Support</option>')
        self.assertContains(response, '<select name="assigned_to"')
        self.assertContains(response, '<input type="text" name="dev_ticket"')
        self.assertContains(response, '<select name="related_to"')
        self.assertContains(response, "User:")
        self.assertContains(response, "User Meta:")
        self.assertContains(response, "Site:")
        self.assertContains(response, "Created:")
        self.assertContains(response, "Updated:")
        self.assertContains(response, "History:")
        self.assertContains(response, '<input type="submit" value="Update" class="btn btn-success">')

        # comment form
        self.assertContains(response, '<textarea name="content"')
        self.assertContains(response, '<select name="visibility"')
        self.assertContains(response, '<input type="submit" value="Comment"')


    def test_ticket_detail_student(self):
        self.client.force_login(self.student)
        uri = reverse("helpme:ticket-detail", args=[self.simple_ticket.uuid])
        response = self.client.get(uri)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ABC")
        self.assertContains(response, "123")
        self.assertContains(response, "Status:")
        self.assertContains(response, "Open")

        # does not contain certain data or an option to update the ticket
        self.assertNotContains(response, '<select name="status"')
        self.assertNotContains(response, '<option value="3" selected>Medium</option>')
        self.assertNotContains(response, '<option value="1" selected>Comment</option>')
        self.assertNotContains(response, '<option value="1" selected>Support</option>')
        self.assertNotContains(response, '<select name="assigned_to"')
        self.assertNotContains(response, '<input type="text" name="dev_ticket"')
        self.assertNotContains(response, '<select name="related_to"')
        self.assertNotContains(response, "User:")
        self.assertNotContains(response, "User Meta:")
        self.assertNotContains(response, "Site:")
        self.assertNotContains(response, "Created:")
        self.assertNotContains(response, "Updated:")
        self.assertNotContains(response, "History:")
        self.assertNotContains(response, '<input type="submit" value="Update">')

        # can leave a comment but cannot set visibility
        self.assertContains(response, '<textarea name="content"')
        self.assertNotContains(response, '<select name="visibility"')
        self.assertContains(response, '<input type="submit" value="Comment"')

        
    def test_ticket_detail_update(self):
        uri = reverse("helpme:ticket-detail", args=[self.simple_ticket.uuid])
        response = self.client.post(uri, {"status": StatusChoices.ACTIVE, "category": app_settings.TICKET_CATEGORIES.COMMENT, "priority": PriorityChoices.MEDIUM}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [(reverse("helpme:ticket-detail", args=[self.simple_ticket.uuid]), 302)])
        self.assertContains(response, '<option value="10" selected>Active</option>')
        self.simple_ticket.refresh_from_db()
        self.assertEqual(self.simple_ticket.status, StatusChoices.ACTIVE)
        self.assertEqual(self.simple_ticket.history[0]["event"], "updated")
        self.assertEqual(self.simple_ticket.history[0]["user"], 1)
        self.assertEqual(self.simple_ticket.history[0]["username"], "supportuser")

        
    def test_comment_creation(self):
        self.assertEqual(Comment.objects.all().count(), 0)
        uri = reverse("helpme-api:create-comment", args=[self.simple_ticket.uuid])
        response = self.client.post(uri, {"content": "This is a test comment", "visibility": VisibilityChoices.REPORTERS}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [(reverse("helpme:ticket-detail", args=[self.simple_ticket.uuid]), 302)])
        
        self.assertContains(response, "supportuser left a comment")
        self.assertContains(response, "This is a test comment")
        self.assertEqual(Comment.objects.all().count(), 1)

        self.simple_ticket.refresh_from_db()
        self.assertEqual(self.simple_ticket.comments.all().count(), 1)
        self.assertEqual(self.simple_ticket.history[0]["event"], "updated")
        self.assertEqual(self.simple_ticket.history[0]["user"], 1)
        self.assertEqual(self.simple_ticket.history[0]["username"], "supportuser")
        self.assertEqual(self.simple_ticket.history[0]["notes"], "supportuser left a comment")


    def test_teams_view_support(self):
        uri = reverse("helpme:team-list")
        response = self.client.get(uri)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Teams")
        self.assertContains(response, '<a href="/support/teams/')
        self.assertContains(response, '> Support </a>')


    def test_teams_view_admin(self):
        self.client.force_login(self.admin)
        uri = reverse("helpme:team-list")
        response = self.client.get(uri)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Manage Teams")
        self.assertContains(response, '<a href="/support/teams/')
        self.assertContains(response, '> Support </a>')


    def test_teams_view_student(self):
        self.client.force_login(self.student)
        uri = reverse("helpme:team-list")
        response = self.client.get(uri)

        # regular user should not have permission to view this page
        self.assertEqual(response.status_code, 403)


    def test_team_detail_support(self):
        uri = reverse("helpme:team-detail", args=[self.support_team.uuid])
        response = self.client.get(uri)

        # lists team details but cannot update them 
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Support")
        self.assertContains(response, "Global team:")
        self.assertContains(response, "False")
        self.assertContains(response, "Sites:")
        self.assertContains(response, "example.com")
        self.assertContains(response, "Categories:")
        self.assertContains(response, "Help")
        self.assertContains(response, "Members:")
        self.assertContains(response, "supportuser")
        self.assertNotContains(response, '<input type="submit" value="Update"')


    def test_team_detail_admin(self):
        self.client.force_login(self.admin)
        uri = reverse("helpme:team-detail", args=[self.support_team.uuid])
        response = self.client.get(uri)

        # form to update team details
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<input type="text" name="name"')
        self.assertContains(response, '<input type="checkbox" name="global_team"')
        self.assertContains(response, '<select name="sites"')
        self.assertContains(response, '<input type="checkbox" class="form-check-input" checked="checked" name="categories" id="id_categories_3" value="3" >')
        self.assertContains(response, '<select name="members"')
        self.assertContains(response, '<input type="submit" value="Update"')
        

    def test_team_detail_student(self):
        self.client.force_login(self.student)
        uri = reverse("helpme:team-detail", args=[self.support_team.uuid])
        response = self.client.get(uri)

        # regular user should not have permission to view this page
        self.assertEqual(response.status_code, 403)
