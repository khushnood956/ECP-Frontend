import React, { createContext, useContext, useState, useEffect } from 'react';
import { initMockData, getMockData } from '../services/mockData';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [scholarships, setScholarships] = useState([]);
  const [universities, setUniversities] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    initMockData();
    setScholarships(getMockData('ecp_scholarships'));
    setUniversities(getMockData('ecp_universities'));
  }, []);

  return (
    <AppContext.Provider value={{
      scholarships, universities,
      searchQuery, setSearchQuery
    }}>
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = () => useContext(AppContext);
