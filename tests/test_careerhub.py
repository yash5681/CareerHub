from datetime import date, timedelta
from django.utils import timezone
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.accounts.models import JobSeekerProfile, RecruiterProfile
from apps.companies.models import Company
from apps.jobs.models import JobCategory, Skill, Job, SavedJob
from apps.resumes.models import Resume
from apps.applications.models import JobApplication, ApplicationStatusHistory
from apps.interviews.models import Interview
from apps.notifications.models import Notification
from apps.payments.models import SubscriptionPlan, Payment, RecruiterSubscription

User = get_user_model()

class CareerHubCoreTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Category
        self.category = JobCategory.objects.create(
            name='Engineering & IT',
            slug='engineering-it',
            icon='fa-solid fa-code'
        )

        # Create Skill
        self.skill = Skill.objects.create(name='Django', slug='django')

        # Create Company
        self.company = Company.objects.create(
            name='TechInnovations India',
            slug='techinnovations-india',
            industry='FinTech',
            city='Bengaluru',
            state='Karnataka',
            about='Next-gen financial architecture.'
        )

        # Create Recruiter
        self.recruiter = User.objects.create_user(
            email='recruiter.test@careerhub.in',
            username='recruiter_test',
            password='TestPassword123!',
            first_name='Kavita',
            last_name='Iyer',
            role=User.Role.RECRUITER
        )
        self.recruiter_profile = RecruiterProfile.objects.create(
            user=self.recruiter,
            company=self.company,
            designation='Talent Acquisition Lead'
        )

        # Free plan & subscription
        self.plan = SubscriptionPlan.objects.create(
            name='Free Starter',
            slug='free-starter',
            price=0,
            job_posting_limit=5
        )
        RecruiterSubscription.objects.create(
            recruiter=self.recruiter,
            plan=self.plan,
            active_until=timezone.now() + timedelta(days=30)
        )

        # Create Job
        self.job = Job.objects.create(
            company=self.company,
            posted_by=self.recruiter,
            title='Senior Django Developer',
            slug='senior-django-developer',
            category=self.category,
            job_type=Job.JobType.FULL_TIME,
            work_mode=Job.WorkMode.REMOTE,
            location_city='Bengaluru',
            location_state='Karnataka',
            experience_min=2,
            experience_max=5,
            salary_min=15,
            salary_max=22,
            description='Build high-concurrency payment microservices.',
            status=Job.Status.PUBLISHED
        )
        self.job.skills.add(self.skill)

        # Create Job Seeker
        self.seeker = User.objects.create_user(
            email='seeker.test@careerhub.in',
            username='seeker_test',
            password='TestPassword123!',
            first_name='Sameer',
            last_name='Verma',
            role=User.Role.JOB_SEEKER
        )
        self.seeker_profile = JobSeekerProfile.objects.create(
            user=self.seeker,
            headline='Python & Django Specialist',
            city='Bengaluru',
            state='Karnataka',
            skills_csv='Python, Django, PostgreSQL'
        )

        # Create Seeker Resume
        self.resume = Resume.objects.create(
            user=self.seeker,
            title='Sameer Verma ATS Resume',
            resume_type=Resume.ResumeType.BUILDER,
            is_primary=True
        )

        # Create Admin
        self.admin = User.objects.create_superuser(
            email='admin.test@careerhub.in',
            username='admin_test',
            password='TestPassword123!',
            first_name='Admin',
            last_name='Root',
            role=User.Role.ADMIN
        )

    # 1. Test Registration
    def test_job_seeker_registration(self):
        resp = self.client.post(reverse('accounts:register_seeker'), {
            'first_name': 'Aarav',
            'last_name': 'Mehta',
            'email': 'aarav.mehta@example.com',
            'phone': '+919876543210',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!',
            'terms_accepted': 'on'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(User.objects.filter(email='aarav.mehta@example.com').exists())
        user = User.objects.get(email='aarav.mehta@example.com')
        self.assertEqual(user.role, User.Role.JOB_SEEKER)
        self.assertTrue(hasattr(user, 'job_seeker_profile'))

    # 2. Test Login & Role Redirection
    def test_login_and_role_redirect(self):
        login_success = self.client.login(username='seeker.test@careerhub.in', password='TestPassword123!')
        self.assertTrue(login_success)
        resp = self.client.get(reverse('dashboard:index'))
        self.assertRedirects(resp, reverse('dashboard:seeker'))

    # 3. Test Job Search & Filters
    def test_job_search_by_keyword_and_filter(self):
        resp = self.client.get(reverse('jobs:list'), {'q': 'Django', 'location': 'Bengaluru'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Senior Django Developer')
        self.assertContains(resp, 'TechInnovations India')

    # 4. Test Job Application Workflow
    def test_job_application_workflow(self):
        self.client.login(username='seeker.test@careerhub.in', password='TestPassword123!')
        resp = self.client.post(reverse('applications:apply', kwargs={'slug': self.job.slug}), {
            'resume': self.resume.id,
            'cover_letter': 'Excited to apply for this backend Django role!'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(JobApplication.objects.filter(job=self.job, applicant=self.seeker).exists())
        app = JobApplication.objects.get(job=self.job, applicant=self.seeker)
        self.assertEqual(app.status, JobApplication.Status.APPLIED)

    # 5. Test Duplicate Application Prevention
    def test_duplicate_application_prevention(self):
        self.client.login(username='seeker.test@careerhub.in', password='TestPassword123!')
        # First application
        JobApplication.objects.create(
            job=self.job,
            applicant=self.seeker,
            resume=self.resume,
            status=JobApplication.Status.APPLIED
        )
        # Attempt second application
        resp = self.client.post(reverse('applications:apply', kwargs={'slug': self.job.slug}), {
            'resume': self.resume.id,
            'cover_letter': 'Trying to apply again'
        })
        # Should redirect back with notice, without creating duplicate
        self.assertEqual(JobApplication.objects.filter(job=self.job, applicant=self.seeker).count(), 1)

    # 6. Test Bookmark / Save Job Toggle
    def test_save_job_toggle(self):
        self.client.login(username='seeker.test@careerhub.in', password='TestPassword123!')
        resp = self.client.post(reverse('jobs:toggle_save', kwargs={'job_id': self.job.id}))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(SavedJob.objects.filter(user=self.seeker, job=self.job).exists())

        # Toggle again to remove
        resp2 = self.client.post(reverse('jobs:toggle_save', kwargs={'job_id': self.job.id}))
        self.assertEqual(resp2.status_code, 200)
        self.assertFalse(SavedJob.objects.filter(user=self.seeker, job=self.job).exists())

    # 7. Test Recruiter Candidate Pipeline & Interview Scheduling
    def test_recruiter_pipeline_and_interview(self):
        app = JobApplication.objects.create(
            job=self.job,
            applicant=self.seeker,
            resume=self.resume,
            status=JobApplication.Status.APPLIED
        )
        self.client.login(username='recruiter.test@careerhub.in', password='TestPassword123!')

        # Quick shortlist
        resp = self.client.get(reverse('applications:quick_status', kwargs={'pk': app.pk, 'new_status': 'shortlisted'}))
        app.refresh_from_db()
        self.assertEqual(app.status, JobApplication.Status.SHORTLISTED)

        # Schedule Interview
        resp2 = self.client.post(reverse('interviews:schedule', kwargs={'application_id': app.pk}), {
            'interview_round': 'Technical Round 1',
            'interview_type': Interview.InterviewType.VIDEO,
            'interview_date': date.today() + timedelta(days=2),
            'interview_time': '14:00',
            'meeting_url': 'https://meet.google.com/test-meet',
            'notes': 'Please keep Python environment ready.'
        })
        self.assertEqual(resp2.status_code, 302)
        app.refresh_from_db()
        self.assertEqual(app.status, JobApplication.Status.INTERVIEW_SCHEDULED)
        self.assertTrue(Interview.objects.filter(application=app, candidate=self.seeker).exists())

    # 8. Test Razorpay Signature Verification & Subscription
    def test_razorpay_payment_signature_verification(self):
        paid_plan = SubscriptionPlan.objects.create(
            name='Growth Pro',
            slug='growth-pro',
            price=2999,
            job_posting_limit=20
        )
        self.client.login(username='recruiter.test@careerhub.in', password='TestPassword123!')

        # Simulated test payment submission
        Payment.objects.create(
            user=self.recruiter,
            plan=paid_plan,
            razorpay_order_id='order_demo_12345',
            amount=2999,
            status=Payment.Status.CREATED
        )

        resp = self.client.post(reverse('payments:verify_payment'), {
            'razorpay_order_id': 'order_demo_12345',
            'razorpay_payment_id': 'pay_demo_verified_123',
            'razorpay_signature': 'sig_test_sandbox_valid'
        })
        self.assertEqual(resp.status_code, 302)

        sub = RecruiterSubscription.objects.get(recruiter=self.recruiter)
        self.assertEqual(sub.plan, paid_plan)
        self.assertTrue(sub.is_active)

    # 9. Test Role Protection (Seeker cannot access Admin Dashboard)
    def test_admin_dashboard_role_protection(self):
        self.client.login(username='seeker.test@careerhub.in', password='TestPassword123!')
        resp = self.client.get(reverse('dashboard:admin_overview'))
        self.assertEqual(resp.status_code, 403)
