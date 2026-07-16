import React, { createContext, useContext, useState, useEffect } from 'react';
import { initMockData, getMockData, updateMockData } from '../services/mockData';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [scholarships, setScholarships] = useState([]);
  const [universities, setUniversities] = useState([]);
  const [applications, setApplications] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    initMockData();
    setScholarships(getMockData('ecp_scholarships'));
    setUniversities(getMockData('ecp_universities'));
    setApplications(getMockData('ecp_applications'));
    setDocuments(getMockData('ecp_documents'));
    setNotifications(getMockData('ecp_notifications'));
  }, []);

  const toggleBookmark = (type, id) => {
    if (type === 'scholarship') {
      const updated = scholarships.map(s => s.id === id ? { ...s, bookmarked: !s.bookmarked } : s);
      setScholarships(updated);
      updateMockData('ecp_scholarships', updated);
    } else if (type === 'university') {
      const updated = universities.map(u => u.id === id ? { ...u, bookmarked: !u.bookmarked } : u);
      setUniversities(updated);
      updateMockData('ecp_universities', updated);
    }
  };

  const addDocument = (doc) => {
    const updated = [...documents, { ...doc, id: Date.now().toString(), uploadDate: new Date().toISOString().split('T')[0], verified: false }];
    setDocuments(updated);
    updateMockData('ecp_documents', updated);
  };

  const deleteDocument = (id) => {
    const updated = documents.filter(d => d.id !== id);
    setDocuments(updated);
    updateMockData('ecp_documents', updated);
  };
  
  const markNotificationRead = (id) => {
    const updated = notifications.map(n => n.id === id ? { ...n, read: true } : n);
    setNotifications(updated);
    updateMockData('ecp_notifications', updated);
  };

  return (
    <AppContext.Provider value={{
      scholarships, universities, applications, documents, notifications,
      toggleBookmark, addDocument, deleteDocument, markNotificationRead,
      searchQuery, setSearchQuery
    }}>
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = () => useContext(AppContext);
