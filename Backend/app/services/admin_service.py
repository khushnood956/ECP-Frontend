from app.models.enums import AgencyVerificationStatus, LeadStatus
from app.repositories.agency_repository import AgencyRepository
from app.repositories.lead_repository import LeadRepository
from app.repositories.scholarship_repository import ScholarshipRepository
from app.repositories.student_profile_repository import StudentProfileRepository
from app.repositories.user_repository import UserRepository
from app.schemas.admin import DashboardStatistics


class AdminService:
    def __init__(
        self,
        user_repo: UserRepository,
        student_repo: StudentProfileRepository,
        agency_repo: AgencyRepository,
        scholarship_repo: ScholarshipRepository,
        lead_repo: LeadRepository
    ):
        self.user_repo = user_repo
        self.student_repo = student_repo
        self.agency_repo = agency_repo
        self.scholarship_repo = scholarship_repo
        self.lead_repo = lead_repo

    async def get_dashboard_statistics(self) -> DashboardStatistics:
        total_users = await self.user_repo.count()
        total_students = await self.student_repo.count()
        total_agencies = await self.agency_repo.count()
        verified_agencies = await self.agency_repo.count(verification_status=AgencyVerificationStatus.VERIFIED)
        pending_agencies = await self.agency_repo.count(verification_status=AgencyVerificationStatus.PENDING)
        suspended_agencies = await self.agency_repo.count(verification_status=AgencyVerificationStatus.REJECTED)
        active_scholarships = await self.scholarship_repo.count(is_active=True)
        total_leads = await self.lead_repo.count()
        leads_new = await self.lead_repo.count(status=LeadStatus.NEW)
        leads_contacted = await self.lead_repo.count(status=LeadStatus.CONTACTED)
        leads_won = await self.lead_repo.count(status=LeadStatus.WON)
        leads_lost = await self.lead_repo.count(status=LeadStatus.LOST)

        return DashboardStatistics(
            total_users=total_users,
            total_students=total_students,
            total_agencies=total_agencies,
            verified_agencies=verified_agencies,
            pending_agencies=pending_agencies,
            suspended_agencies=suspended_agencies,
            active_scholarships=active_scholarships,
            total_leads=total_leads,
            leads_new=leads_new,
            leads_contacted=leads_contacted,
            leads_won=leads_won,
            leads_lost=leads_lost,
        )
