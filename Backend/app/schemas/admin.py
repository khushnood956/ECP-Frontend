from pydantic import BaseModel


class DashboardStatistics(BaseModel):
    total_users: int
    total_students: int
    total_agencies: int
    verified_agencies: int
    pending_agencies: int
    suspended_agencies: int
    active_scholarships: int
    total_leads: int
    leads_new: int
    leads_contacted: int
    leads_won: int
    leads_lost: int
