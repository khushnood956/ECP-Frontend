import { apiClient } from './apiClient';

export class StudentAPI {
  static async getStudentProfile(id) {
    const response = await apiClient.get(`/student-profiles/${id}`);
    return response.data;
  }

  static async getDocuments() {
    const response = await apiClient.get('/student-profiles/documents');
    return response.data.data;
  }

  static async createDocument(formData) {
    const response = await apiClient.post('/student-profiles/documents', formData, {
      headers: {
        'Content-Type': undefined
      }
    });
    return response.data.data;
  }

  static async getDocumentDownloadUrl(id) {
    const response = await apiClient.get(`/student-profiles/documents/${id}/download`);
    return response.data.data.download_url;
  }

  static async deleteDocument(id) {
    const response = await apiClient.delete(`/student-profiles/documents/${id}`);
    return response.data;
  }

  static async getBookmarks() {
    const response = await apiClient.get('/bookmarks');
    return response.data.data;
  }

  static async createBookmark(bookmarkType, scholarshipId = null, universityId = null) {
    const response = await apiClient.post('/bookmarks', {
      bookmark_type: bookmarkType,
      scholarship_id: scholarshipId,
      university_id: universityId
    });
    return response.data.data;
  }

  static async deleteBookmark(id) {
    const response = await apiClient.delete(`/bookmarks/${id}`);
    return response.data;
  }

  static async getNotifications() {
    const response = await apiClient.get('/notifications');
    return response.data.data;
  }

  static async markNotificationRead(id) {
    const response = await apiClient.patch(`/notifications/${id}/read`);
    return response.data.data;
  }

  static async markAllNotificationsRead() {
    const response = await apiClient.post('/notifications/read-all');
    return response.data;
  }

  static async deleteNotification(id) {
    const response = await apiClient.delete(`/notifications/${id}`);
    return response.data;
  }
}
