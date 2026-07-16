export const mockScholarships = [
  { id: '1', title: 'Global Excellence Scholarship', provider: 'University of Toronto', amount: '$10,000', deadline: '2026-09-01', type: 'Merit-based', bookmarked: true },
  { id: '2', title: 'Women in Tech Grant', provider: 'Tech Forward', amount: '$5,000', deadline: '2026-10-15', type: 'Diversity', bookmarked: false },
  { id: '3', title: 'International Student Fund', provider: 'University of Melbourne', amount: 'Full Tuition', deadline: '2026-08-30', type: 'Need-based', bookmarked: true }
];

export const mockUniversities = [
  { id: '1', name: 'University of Toronto', location: 'Canada', ranking: 'Top 50', type: 'Public', bookmarked: false },
  { id: '2', name: 'University of Melbourne', location: 'Australia', ranking: 'Top 100', type: 'Public', bookmarked: true },
  { id: '3', name: 'MIT', location: 'USA', ranking: 'Top 10', type: 'Private', bookmarked: false }
];

export const mockApplications = [
  { id: '1', university: 'University of Toronto', program: 'MSc Computer Science', intake: 'Fall 2026', status: 'Submitted', date: '2026-06-15' },
  { id: '2', university: 'University of Melbourne', program: 'Master of Data Science', intake: 'Spring 2027', status: 'In Review', date: '2026-07-01' }
];

export const mockDocuments = [
  { id: '1', name: 'IELTS_Certificate.pdf', type: 'Language Test', uploadDate: '2026-07-10', verified: true },
  { id: '2', name: 'Bachelors_Transcript.pdf', type: 'Academic', uploadDate: '2026-07-12', verified: true },
  { id: '3', name: 'Passport_Copy.pdf', type: 'ID', uploadDate: '2026-07-14', verified: false }
];

export const mockNotifications = [
  { id: '1', title: 'Application Update', message: 'Your application to University of Toronto is submitted.', time: '2 hours ago', read: false },
  { id: '2', title: 'Document Verified', message: 'Your IELTS Certificate has been verified.', time: '1 day ago', read: true }
];

// Helper to init local storage
export const initMockData = () => {
  if (!localStorage.getItem('ecp_scholarships')) {
    localStorage.setItem('ecp_scholarships', JSON.stringify(mockScholarships));
  }
  if (!localStorage.getItem('ecp_universities')) {
    localStorage.setItem('ecp_universities', JSON.stringify(mockUniversities));
  }
  if (!localStorage.getItem('ecp_applications')) {
    localStorage.setItem('ecp_applications', JSON.stringify(mockApplications));
  }
  if (!localStorage.getItem('ecp_documents')) {
    localStorage.setItem('ecp_documents', JSON.stringify(mockDocuments));
  }
  if (!localStorage.getItem('ecp_notifications')) {
    localStorage.setItem('ecp_notifications', JSON.stringify(mockNotifications));
  }
};

export const getMockData = (key) => {
  return JSON.parse(localStorage.getItem(key)) || [];
};

export const updateMockData = (key, data) => {
  localStorage.setItem(key, JSON.stringify(data));
};
