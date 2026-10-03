import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.accounts.models import (
    JobSeekerProfile, RecruiterProfile, Education,
    Experience, Project, Certification, Language
)
from apps.companies.models import Company, CompanyReview
from apps.jobs.models import JobCategory, Skill, Location, Job, SavedJob
from apps.resumes.models import Resume
from apps.applications.models import JobApplication, ApplicationStatusHistory
from apps.interviews.models import Interview
from apps.messaging.models import Conversation, Message
from apps.notifications.models import Notification
from apps.payments.models import SubscriptionPlan, Payment, RecruiterSubscription
from apps.blog.models import BlogCategory, BlogPost
from apps.core.models import SiteSetting

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds realistic Indian job market demo data for CareerHub'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting CareerHub Indian Job Market data seeding..."))

        # 1. Site Settings
        SiteSetting.objects.get_or_create(
            site_name='CareerHub',
            defaults={
                'tagline': 'Connecting India’s Tech Talent with Premier Opportunities',
                'contact_email': 'pyash7571@gmail.com',
                'contact_phone': '+91 9023433407',
                'address': 'Himatnagar, Gujarat, India',
            }
        )

        # 2. Admin Superuser
        admin_email = 'pyash7571@gmail.com'
        admin_user = User.objects.filter(email=admin_email).first()
        if not admin_user:
            admin_user = User.objects.create_superuser(
                email=admin_email,
                username='yash',
                password='Admin@CareerHub2026',
                first_name='Yash',
                last_name='Prajapati',
                phone='+919023433407'
            )
            self.stdout.write(self.style.SUCCESS(f"Superuser created: {admin_email} / Admin@CareerHub2026"))
        else:
            self.stdout.write(f"Superuser already exists: {admin_email}")

        # 3. Job Categories
        categories_data = [
            ("Software & Engineering", "fa-solid fa-code", "Full-Stack, Backend, Frontend, Cloud & DevOps opportunities", 1),
            ("Data Science & AI", "fa-solid fa-brain", "Machine Learning, LLMs, Computer Vision & Big Data Analytics", 2),
            ("FinTech & Banking", "fa-solid fa-chart-line", "Financial Engineering, Payments, Risk & Investment Banking", 3),
            ("Product & Design", "fa-solid fa-compass-drafting", "UI/UX Architecture, Visual Design & Product Management", 4),
            ("Cloud & Infrastructure", "fa-solid fa-server", "AWS, GCP, Kubernetes, SRE & Cyber Security Engineering", 5),
            ("Marketing & Growth", "fa-solid fa-bullhorn", "Digital Marketing, SEO, Content & Growth Hacking", 6),
            ("Sales & Business Dev", "fa-solid fa-handshake", "Enterprise B2B Sales, Account Executives & Partnerships", 7),
            ("Human Resources & Talent", "fa-solid fa-users", "Technical Recruitment, HRBP, Talent Ops & People Management", 8),
        ]
        created_categories = {}
        for name, icon, desc, order in categories_data:
            cat, _ = JobCategory.objects.get_or_create(
                name=name,
                defaults={'icon': icon, 'description': desc, 'order': order, 'is_featured': True}
            )
            created_categories[name] = cat

        # 4. Indian Locations
        locations_data = [
            ("Karnataka", "Bengaluru", True),
            ("Maharashtra", "Pune", True),
            ("Maharashtra", "Mumbai", True),
            ("Telangana", "Hyderabad", True),
            ("Haryana", "Gurugram", True),
            ("Uttar Pradesh", "Noida", True),
            ("Tamil Nadu", "Chennai", True),
            ("Gujarat", "Ahmedabad", True),
            ("Gujarat", "Surat", False),
            ("Gujarat", "Vadodara", False),
            ("West Bengal", "Kolkata", True),
        ]
        for state, city, popular in locations_data:
            Location.objects.get_or_create(state=state, city=city, defaults={'is_popular': popular})

        # 5. Technical Skills
        skills_list = [
            "Python", "Django", "PostgreSQL", "React", "Node.js", "Docker", "AWS",
            "Kubernetes", "Redis", "Celery", "FastAPI", "Machine Learning", "TypeScript",
            "Next.js", "GraphQL", "Tailwind CSS", "Java", "Spring Boot", "Go", "SQL",
            "Git", "REST APIs", "Microservices", "System Design", "CI/CD", "DevOps"
        ]
        created_skills = {}
        for s_name in skills_list:
            sk, _ = Skill.objects.get_or_create(name=s_name)
            created_skills[s_name] = sk

        # 6. Subscription Plans
        free_plan, _ = SubscriptionPlan.objects.get_or_create(
            slug='free-starter',
            defaults={
                'name': 'Free Starter',
                'price': 0,
                'billing_period': SubscriptionPlan.BillingPeriod.MONTHLY,
                'job_posting_limit': 2,
                'featured_job_limit': 0,
                'candidate_contacts_limit': 15,
                'description': 'Essential toolkit for growing Indian startups and hiring managers.',
                'features_list': '2 Active Job Postings\nCandidate Application Pipeline\nDirect In-App Messaging\nStandard Community Support',
                'is_popular': False,
                'order': 1
            }
        )

        pro_plan, _ = SubscriptionPlan.objects.get_or_create(
            slug='professional-recruiter',
            defaults={
                'name': 'Professional Recruiter',
                'price': 2499,
                'billing_period': SubscriptionPlan.BillingPeriod.MONTHLY,
                'job_posting_limit': 15,
                'featured_job_limit': 4,
                'candidate_contacts_limit': 100,
                'description': 'Tailored for scaling technology firms and fast-growing agencies.',
                'features_list': '15 Active Job Postings\n4 Featured Homepage Listings\nPriority Candidate Matching Engine\nUnlimited Direct Candidate Messaging\nDedicated Account Support',
                'is_popular': True,
                'order': 2
            }
        )

        ent_plan, _ = SubscriptionPlan.objects.get_or_create(
            slug='enterprise-business',
            defaults={
                'name': 'Enterprise Business',
                'price': 6999,
                'billing_period': SubscriptionPlan.BillingPeriod.MONTHLY,
                'job_posting_limit': 50,
                'featured_job_limit': 15,
                'candidate_contacts_limit': 500,
                'description': 'Comprehensive hiring architecture for mid-market and enterprise employers.',
                'features_list': '50 Active Job Postings\n15 Featured Placements\nCustom Employer Branding Banner\nCandidate Resume Database Search\nMulti-Recruiter Team Accounts\n24/7 SLA Priority Phone Support',
                'is_popular': False,
                'order': 3
            }
        )

        # 7. Seed Companies
        companies_data = [
            {
                'name': 'Razorpay Software',
                'tagline': 'The Future of Payments in India',
                'industry': 'FinTech & Payments',
                'size': Company.CompanySize.LARGE,
                'city': 'Bengaluru',
                'state': 'Karnataka',
                'about': 'Razorpay is India’s leading full-stack financial solutions company enabling digital businesses to accept, process and disburse payments effortlessly.',
                'benefits': 'Comprehensive Medical Insurance, Hybrid Work Options, Wellness Allowances, Generous ESOP Pool, Professional Development Stipend.',
                'is_verified': True,
                'is_featured': True,
                'founded': 2014,
                'website': 'https://razorpay.com'
            },
            {
                'name': 'Infosys Technologies',
                'tagline': 'Navigate Your Next',
                'industry': 'IT Services & Consulting',
                'size': Company.CompanySize.ENTERPRISE,
                'city': 'Bengaluru',
                'state': 'Karnataka',
                'about': 'Infosys is a global leader in next-generation digital services and consulting, enabling clients in more than 56 countries to navigate digital transformation.',
                'benefits': 'Global Relocation Support, Continuous Learning Programs, Health Insurance, Cafeteria & Fitness Centers.',
                'is_verified': True,
                'is_featured': True,
                'founded': 1981,
                'website': 'https://infosys.com'
            },
            {
                'name': 'Tata Consultancy Services',
                'tagline': 'Building on Belief',
                'industry': 'Information Technology',
                'size': Company.CompanySize.ENTERPRISE,
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'about': 'TCS is an IT services, consulting and business solutions organization that has been partnering with many of the world’s largest businesses for 50 years.',
                'benefits': 'Retirement Provident Fund, Medical Coverage for Dependents, On-site Training, Global Mobility.',
                'is_verified': True,
                'is_featured': True,
                'founded': 1968,
                'website': 'https://tcs.com'
            },
            {
                'name': 'Zomato Media',
                'tagline': 'Better Food for More People',
                'industry': 'FoodTech & Hyperlocal Delivery',
                'size': Company.CompanySize.LARGE,
                'city': 'Gurugram',
                'state': 'Haryana',
                'about': 'Zomato is an Indian multinational restaurant aggregator and food delivery company operating across thousands of Indian cities.',
                'benefits': 'Catered Daily Meals, ESOPs, Vibrant Culture, Parental Leaves, Free Gym Memberships.',
                'is_verified': True,
                'is_featured': True,
                'founded': 2008,
                'website': 'https://zomato.com'
            },
            {
                'name': 'Zerodha Broking',
                'tagline': 'Free Online Trading & Discount Brokerage',
                'industry': 'FinTech & Capital Markets',
                'size': Company.CompanySize.MEDIUM,
                'city': 'Bengaluru',
                'state': 'Karnataka',
                'about': 'Zerodha pioneered the discount broking model in India and is currently the largest retail stockbroker in India by active client base.',
                'benefits': 'High Engineering Autonomy, Remote-First Options, Competitive Salary, No Arbitrary Hours.',
                'is_verified': True,
                'is_featured': True,
                'founded': 2010,
                'website': 'https://zerodha.com'
            },
        ]

        created_companies = {}
        for cdata in companies_data:
            c, _ = Company.objects.get_or_create(
                name=cdata['name'],
                defaults={
                    'tagline': cdata['tagline'],
                    'industry': cdata['industry'],
                    'company_size': cdata['size'],
                    'city': cdata['city'],
                    'state': cdata['state'],
                    'about': cdata['about'],
                    'benefits': cdata['benefits'],
                    'is_verified': cdata['is_verified'],
                    'is_featured': cdata['is_featured'],
                    'founded_year': cdata['founded'],
                    'website': cdata['website'],
                    'email': f"contact@{cdata['name'].lower().replace(' ', '')}.in"
                }
            )
            created_companies[cdata['name']] = c

        # 8. Seed Recruiters
        recruiters_data = [
            ("priya.nair@razorpay.com", "Priya", "Nair", "Razorpay Software", "Lead Technical Recruiter", pro_plan),
            ("arjun.patel@infosys.com", "Arjun", "Patel", "Infosys Technologies", "Senior Talent Partner", ent_plan),
            ("neha.singh@zomato.com", "Neha", "Singh", "Zomato Media", "Engineering Hiring Lead", pro_plan),
            ("karthik.ram@zerodha.com", "Karthik", "Ramanathan", "Zerodha Broking", "Head of People & Culture", free_plan),
        ]
        created_recruiters = []
        for email, fn, ln, comp_name, desig, plan in recruiters_data:
            u = User.objects.filter(email=email).first()
            if not u:
                u = User.objects.create_user(
                    email=email,
                    username=email.split('@')[0],
                    password='Password@123',
                    first_name=fn,
                    last_name=ln,
                    role=User.Role.RECRUITER,
                    phone='+919876512345',
                    is_verified=True
                )
            company = created_companies[comp_name]
            RecruiterProfile.objects.get_or_create(
                user=u,
                defaults={'company': company, 'designation': desig, 'is_company_admin': True}
            )
            # Create subscription
            RecruiterSubscription.objects.get_or_create(
                recruiter=u,
                defaults={'plan': plan, 'active_until': timezone.now() + timedelta(days=90), 'is_active': True}
            )
            created_recruiters.append((u, company))

        # 9. Seed Job Postings
        jobs_data = [
            {
                'title': 'Senior Full-Stack Django & React Engineer',
                'company': 'Razorpay Software',
                'category': 'Software & Engineering',
                'job_type': Job.JobType.FULL_TIME,
                'work_mode': Job.WorkMode.HYBRID,
                'city': 'Bengaluru',
                'state': 'Karnataka',
                'exp_min': 3.0, 'exp_max': 6.0,
                'sal_min': 18.0, 'sal_max': 28.0,
                'skills': ['Python', 'Django', 'React', 'PostgreSQL', 'Docker', 'REST APIs'],
                'is_featured': True,
                'desc': 'We are seeking an experienced Full-Stack Django Developer to architect high-throughput payment checkout experiences.',
                'resp': '- Design and build scalable REST APIs with Django and PostgreSQL.\n- Partner with product managers to launch UPI and international payment routes.\n- Write clean, maintainable, and high-performance Python code.',
                'req': '- 3+ years experience with Django and modern JavaScript (React).\n- Strong understanding of relational databases and PostgreSQL query tuning.\n- Familiarity with Docker and AWS cloud deployments.'
            },
            {
                'title': 'Cloud DevOps & Kubernetes Specialist',
                'company': 'Infosys Technologies',
                'category': 'Cloud & Infrastructure',
                'job_type': Job.JobType.FULL_TIME,
                'work_mode': Job.WorkMode.ON_SITE,
                'city': 'Pune',
                'state': 'Maharashtra',
                'exp_min': 4.0, 'exp_max': 8.0,
                'sal_min': 15.0, 'sal_max': 24.0,
                'skills': ['AWS', 'Kubernetes', 'Docker', 'CI/CD', 'DevOps'],
                'is_featured': True,
                'desc': 'Lead the cloud transformation and container orchestration practices for our global enterprise clientele.',
                'resp': '- Deploy and maintain multi-region Kubernetes clusters on AWS.\n- Build robust GitOps CI/CD pipelines.\n- Ensure 99.99% system availability and security compliance.',
                'req': '- Hands-on mastery of Docker, Helm, and Kubernetes.\n- Proven expertise with AWS VPC, EKS, and Terraform.\n- Strong Linux scripting skills.'
            },
            {
                'title': 'Junior Python Backend Developer',
                'company': 'Zerodha Broking',
                'category': 'Software & Engineering',
                'job_type': Job.JobType.FULL_TIME,
                'work_mode': Job.WorkMode.REMOTE,
                'city': 'Bengaluru',
                'state': 'Karnataka',
                'exp_min': 0.0, 'exp_max': 2.0,
                'sal_min': 8.0, 'sal_max': 12.0,
                'skills': ['Python', 'PostgreSQL', 'Redis', 'SQL'],
                'is_featured': False,
                'desc': 'Fresher friendly opening! Join our core market trading infrastructure engineering team.',
                'resp': '- Assist in developing backend microservices in Python.\n- Optimize SQL database queries for real-time market order feeds.\n- Collaborate in code reviews and automated testing.',
                'req': '- Solid grasp of Python data structures and algorithms.\n- Basic knowledge of relational databases and SQL.\n- High curiosity and problem-solving drive.'
            },
            {
                'title': 'Senior Product Designer (UI/UX)',
                'company': 'Zomato Media',
                'category': 'Product & Design',
                'job_type': Job.JobType.FULL_TIME,
                'work_mode': Job.WorkMode.ON_SITE,
                'city': 'Gurugram',
                'state': 'Haryana',
                'exp_min': 3.0, 'exp_max': 6.0,
                'sal_min': 16.0, 'sal_max': 25.0,
                'skills': ['TypeScript', 'React'],
                'is_featured': True,
                'desc': 'Shape the everyday dining and delivery discovery journeys for tens of millions of Indian consumers.',
                'resp': '- Create intuitive user flows, wireframes, and high-fidelity prototypes.\n- Conduct qualitative user research and usability testing.\n- Establish and evolve design system components.',
                'req': '- Proven portfolio showcasing mobile app and responsive web design.\n- Mastery of Figma and design system tokens.\n- Empathy for diverse user personas across Tier 1, 2 & 3 cities.'
            },
            {
                'title': 'Data Scientist — Machine Learning & LLMs',
                'company': 'Razorpay Software',
                'category': 'Data Science & AI',
                'job_type': Job.JobType.FULL_TIME,
                'work_mode': Job.WorkMode.HYBRID,
                'city': 'Bengaluru',
                'state': 'Karnataka',
                'exp_min': 2.0, 'exp_max': 5.0,
                'sal_min': 20.0, 'sal_max': 32.0,
                'skills': ['Python', 'Machine Learning', 'SQL'],
                'is_featured': True,
                'desc': 'Deploy intelligent fraud detection algorithms, merchant transaction scoring, and AI workflow automation.',
                'resp': '- Build and operationalize predictive machine learning pipelines.\n- Fine-tune domain-specific LLMs for automated merchant customer support.\n- Analyze multi-terabyte transactional datasets.',
                'req': '- Strong proficiency in Python, PyTorch/TensorFlow, and Pandas.\n- Deep mathematical grounding in statistics and probability.\n- Experience deploying models via FastAPI microservices.'
            },
        ]

        created_jobs = []
        for jdata in jobs_data:
            company = created_companies[jdata['company']]
            recruiter_user = company.recruiters.first().user
            cat = created_categories[jdata['category']]
            
            job = Job.objects.filter(title=jdata['title'], company=company).first()
            if not job:
                job = Job.objects.create(
                    company=company,
                    posted_by=recruiter_user,
                    title=jdata['title'],
                    category=cat,
                    job_type=jdata['job_type'],
                    work_mode=jdata['work_mode'],
                    location_city=jdata['city'],
                    location_state=jdata['state'],
                    experience_min=jdata['exp_min'],
                    experience_max=jdata['exp_max'],
                    salary_min=jdata['sal_min'],
                    salary_max=jdata['sal_max'],
                    description=jdata['desc'],
                    responsibilities=jdata['resp'],
                    requirements=jdata['req'],
                    benefits=company.benefits,
                    status=Job.Status.PUBLISHED,
                    is_featured=jdata['is_featured'],
                    openings_count=random.randint(1, 4),
                    application_deadline=timezone.now().date() + timedelta(days=30),
                    views_count=random.randint(45, 320)
                )
                for sk_name in jdata['skills']:
                    if sk_name in created_skills:
                        job.skills.add(created_skills[sk_name])
            created_jobs.append(job)

        # 10. Seed Job Seekers with Complete Indian Profiles
        seekers_data = [
            {
                'email': 'rahul.sharma@example.com', 'fn': 'Rahul', 'ln': 'Sharma',
                'headline': 'Senior Django & Python Developer | 4+ Yrs | AWS Specialist',
                'city': 'Bengaluru', 'state': 'Karnataka', 'exp': 4.5, 'sal_cur': 14.0, 'sal_exp': 22.0,
                'skills': 'Python, Django, PostgreSQL, Docker, AWS, React, Celery, Redis',
                'summary': 'Full-stack software developer with 4.5 years of experience building high-scale Python web applications and microservices in Indian FinTech startups.'
            },
            {
                'email': 'ananya.deshmukh@example.com', 'fn': 'Ananya', 'ln': 'Deshmukh',
                'headline': 'Cloud Architect & DevOps Engineer | Kubernetes Certified',
                'city': 'Pune', 'state': 'Maharashtra', 'exp': 5.0, 'sal_cur': 16.0, 'sal_exp': 25.0,
                'skills': 'AWS, Kubernetes, Docker, CI/CD, Terraform, Linux, Python',
                'summary': 'Passionate DevOps and site reliability engineer specializing in automating cloud infrastructure, zero-downtime rollouts, and multi-cloud architectures.'
            },
            {
                'email': 'amit.patel@example.com', 'fn': 'Amit', 'ln': 'Patel',
                'headline': 'Junior Backend Engineer & Open Source Contributor',
                'city': 'Ahmedabad', 'state': 'Gujarat', 'exp': 1.0, 'sal_cur': 6.0, 'sal_exp': 10.0,
                'skills': 'Python, Django, PostgreSQL, Git, REST APIs',
                'summary': 'Dedicated computer science graduate with 1 year professional experience in backend REST API design and relational database optimization.'
            }
        ]

        created_seekers = []
        for sdata in seekers_data:
            u = User.objects.filter(email=sdata['email']).first()
            if not u:
                u = User.objects.create_user(
                    email=sdata['email'],
                    username=sdata['email'].split('@')[0],
                    password='Password@123',
                    first_name=sdata['fn'],
                    last_name=sdata['ln'],
                    role=User.Role.JOB_SEEKER,
                    phone='+919876599999',
                    is_verified=True
                )
            profile, _ = JobSeekerProfile.objects.get_or_create(
                user=u,
                defaults={
                    'headline': sdata['headline'],
                    'city': sdata['city'],
                    'state': sdata['state'],
                    'total_experience_years': sdata['exp'],
                    'current_salary': sdata['sal_cur'],
                    'expected_salary': sdata['sal_exp'],
                    'skills_csv': sdata['skills'],
                    'summary': sdata['summary'],
                    'work_preference': JobSeekerProfile.WorkPreference.HYBRID,
                    'notice_period_days': 30,
                    'linkedin_url': f"https://linkedin.com/in/{sdata['fn'].lower()}-{sdata['ln'].lower()}",
                    'github_url': f"https://github.com/{sdata['fn'].lower()}{sdata['ln'].lower()}",
                }
            )

            # Education
            Education.objects.get_or_create(
                profile=profile,
                degree='Bachelor of Technology (B.Tech)',
                institution='National Institute of Technology',
                field_of_study='Computer Science and Engineering',
                start_year=2016,
                end_year=2020,
                defaults={'grade': '8.6 CGPA'}
            )

            # Work Experience
            Experience.objects.get_or_create(
                profile=profile,
                company_name='TechVentures India',
                job_title='Software Development Engineer',
                defaults={
                    'start_date': date(2021, 6, 1),
                    'is_current': True,
                    'location': sdata['city'],
                    'description': 'Designed high-throughput payment ingestion pipelines handling 5,000+ requests per second.'
                }
            )

            # Project
            Project.objects.get_or_create(
                profile=profile,
                title='Distributed Task Dispatcher',
                defaults={
                    'technologies': 'Python, Celery, Redis, Docker',
                    'project_url': 'https://github.com/example/dispatcher',
                    'description': 'Asynchronous job queue and notification engine with automatic retry policies and Prometheus metrics.'
                }
            )

            # Resume
            resume, _ = Resume.objects.get_or_create(
                user=u,
                title=f"{sdata['fn']} {sdata['ln']} ATS Resume 2026",
                defaults={
                    'resume_type': Resume.ResumeType.BUILDER,
                    'is_primary': True,
                    'template_name': 'modern'
                }
            )

            profile.calculate_completion()
            created_seekers.append((u, resume))

        # 11. Seed Applications in Various Pipeline Stages
        target_job = created_jobs[0]
        test_seeker, test_resume = created_seekers[0]

        app1, _ = JobApplication.objects.get_or_create(
            job=target_job,
            applicant=test_seeker,
            defaults={
                'resume': test_resume,
                'status': JobApplication.Status.INTERVIEW_SCHEDULED,
                'cover_letter': 'I have built multiple payment checkout systems with Django and PostgreSQL at high volume. Looking forward to discussing this role!',
                'recruiter_notes': 'Candidate exhibits strong system design fundamentals and relevant Python skills. Proceed with technical round.'
            }
        )

        ApplicationStatusHistory.objects.get_or_create(
            application=app1,
            previous_status=JobApplication.Status.APPLIED,
            new_status=JobApplication.Status.INTERVIEW_SCHEDULED,
            defaults={'changed_by': target_job.posted_by, 'comment': 'Candidate profile shortlisted. Scheduled Technical Round.'}
        )

        # 12. Seed Interview
        Interview.objects.get_or_create(
            application=app1,
            defaults={
                'job': target_job,
                'candidate': test_seeker,
                'recruiter': target_job.posted_by,
                'interview_round': 'Technical Round 1: System Design',
                'interview_type': Interview.InterviewType.VIDEO,
                'interview_date': timezone.now().date() + timedelta(days=2),
                'interview_time': timezone.now().time().replace(hour=14, minute=30, second=0),
                'meeting_url': 'https://meet.google.com/xyz-careerhub-demo',
                'notes': 'Please be prepared to walk through your previous Django architecture choices.',
                'status': Interview.Status.SCHEDULED
            }
        )

        # 13. Seed Messaging Conversation
        conv, _ = Conversation.objects.get_or_create(
            seeker=test_seeker,
            recruiter=target_job.posted_by,
            job=target_job
        )
        Message.objects.get_or_create(
            conversation=conv,
            sender=target_job.posted_by,
            content=f"Hello {test_seeker.first_name}, thank you for applying to the {target_job.title} role! We were impressed by your resume and scheduled a technical round on Google Meet."
        )
        Message.objects.get_or_create(
            conversation=conv,
            sender=test_seeker,
            content="Thank you Priya! I have confirmed the calendar slot and am looking forward to our discussion."
        )

        # 14. Seed Company Reviews
        CompanyReview.objects.get_or_create(
            company=created_companies['Razorpay Software'],
            user=test_seeker,
            defaults={
                'rating': 5,
                'title': 'Exceptional Engineering Ownership & Rapid Learning',
                'pros': 'High autonomy, smart colleagues, modern tech stack with Python/Django, generous health benefits.',
                'cons': 'Fast-paced sprints require disciplined prioritization.',
                'review_text': 'One of the finest places in India to solve core FinTech and high-scale backend problems.',
                'is_approved': True
            }
        )

        # 15. Seed Career Blog Posts
        blog_cat, _ = BlogCategory.objects.get_or_create(name='Interview Preparation')
        blog_cat2, _ = BlogCategory.objects.get_or_create(name='Career Guidance')

        BlogPost.objects.get_or_create(
            title='How to Crack Django & Python System Design Interviews in India (2026)',
            defaults={
                'category': blog_cat,
                'author': admin_user,
                'excerpt': 'Key architectural patterns, database indexing tricks, and concurrency handling required for Senior Python roles in top Indian product startups.',
                'content': '<p>System design interviews for Python engineers in India have evolved dramatically over the last few years. Companies are no longer asking trivial questions about syntax; they want to see how you handle millions of daily active users, connection pools, and database read-replicas.</p><h4>1. Understand ORM Query Costs</h4><p>Always avoid N+1 queries by leveraging <code>select_related</code> and <code>prefetch_related</code>. In high-traffic environments, poorly indexed foreign keys can quickly lock your database.</p><h4>2. Asynchronous Workers</h4><p>Never perform heavy operations inside the HTTP request-response cycle. Offload email dispatch, PDF rendering, and third-party webhook calls to background workers using Celery and Redis.</p>',
                'is_published': True,
                'views_count': 340
            }
        )

        BlogPost.objects.get_or_create(
            title='10 High-Impact Words to Transform Your Software Engineering Resume',
            defaults={
                'category': blog_cat2,
                'author': admin_user,
                'excerpt': 'Replace passive verbs with high-impact action statements that capture recruiter attention and pass ATS parsers seamlessly.',
                'content': '<p>Recruiters look at hundreds of resumes every day. To stand out, phrase your accomplishments with measurable impact: what problem did you tackle, what action did you execute, and what business metrics did you improve?</p>',
                'is_published': True,
                'views_count': 210
            }
        )

        # 16. Seed Notifications
        Notification.objects.get_or_create(
            recipient=test_seeker,
            title='Interview Scheduled: Razorpay Software',
            defaults={
                'message': 'Your Technical Round 1 for Senior Full-Stack Django Engineer is confirmed for Google Meet.',
                'notification_type': Notification.NotificationType.INTERVIEW_SCHEDULED,
                'link_url': '/interviews/my/'
            }
        )

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully!"))
        self.stdout.write(self.style.SUCCESS("Demo Credentials:"))
        self.stdout.write("  Admin: admin@careerhub.in / Admin@CareerHub2026")
        self.stdout.write("  Recruiter: priya.nair@razorpay.com / Password@123")
        self.stdout.write("  Job Seeker: rahul.sharma@example.com / Password@123")
