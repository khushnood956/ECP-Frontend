const USERS_KEY = 'educonsultant_users';

// Helper for realistic network delay
const delay = (ms = 600) => new Promise(resolve => setTimeout(resolve, ms));

const getStoredUsers = () => {
  const users = localStorage.getItem(USERS_KEY);
  if (!users) {
    // Seed default user
    const defaultUsers = [
      {
        name: 'Alex Johnson',
        email: 'student@test.com',
        password: 'Password123',
        profileImg: 'https://api.dicebear.com/7.x/adventurer/svg?seed=Alex',
        degreePreference: 'Master of Computer Science',
        ieltsScore: '7.5'
      }
    ];
    localStorage.setItem(USERS_KEY, JSON.stringify(defaultUsers));
    return defaultUsers;
  }
  return JSON.parse(users);
};

export const api = {
  login: async (email, password) => {
    await delay();
    const users = getStoredUsers();
    const user = users.find(u => u.email.toLowerCase() === email.toLowerCase());
    
    if (!user) {
      throw new Error('User not found. Please register first.');
    }
    if (user.password !== password) {
      throw new Error('Invalid credentials. Please try again.');
    }
    
    // Success - omit password from returned user details
    const { password: _, ...userProfile } = user;
    const token = `mock-jwt-token-${btoa(email)}`;
    
    return { user: userProfile, token };
  },

  register: async (userData) => {
    await delay();
    const users = getStoredUsers();
    
    if (users.some(u => u.email.toLowerCase() === userData.email.toLowerCase())) {
      throw new Error('An account with this email already exists.');
    }

    const newUser = {
      name: userData.name,
      email: userData.email,
      password: userData.password,
      profileImg: userData.profileImg || `https://api.dicebear.com/7.x/adventurer/svg?seed=${encodeURIComponent(userData.name)}`,
      degreePreference: userData.degreePreference || 'Master of Computer Science',
      ieltsScore: userData.ieltsScore || '7.0'
    };

    users.push(newUser);
    localStorage.setItem(USERS_KEY, JSON.stringify(users));

    const { password: _, ...userProfile } = newUser;
    const token = `mock-jwt-token-${btoa(newUser.email)}`;

    return { user: userProfile, token };
  },

  updateProfile: async (token, profileData) => {
    await delay();
    if (!token) throw new Error('Unauthorized');
    
    // Decode email from mock token
    const emailBase64 = token.replace('mock-jwt-token-', '');
    let email;
    try {
      email = atob(emailBase64);
    } catch {
      throw new Error('Invalid session token');
    }

    const users = getStoredUsers();
    const userIndex = users.findIndex(u => u.email.toLowerCase() === email.toLowerCase());

    if (userIndex === -1) {
      throw new Error('User not found.');
    }

    const originalEmail = users[userIndex].email;
    const newEmail = profileData.email || originalEmail;

    if (newEmail.toLowerCase() !== originalEmail.toLowerCase()) {
      if (users.some((u, idx) => idx !== userIndex && u.email.toLowerCase() === newEmail.toLowerCase())) {
        throw new Error('The email address is already in use by another user.');
      }
    }

    users[userIndex] = {
      ...users[userIndex],
      name: profileData.name || users[userIndex].name,
      email: newEmail,
      degreePreference: profileData.degreePreference || users[userIndex].degreePreference,
      ieltsScore: profileData.ieltsScore || users[userIndex].ieltsScore,
      profileImg: profileData.profileImg || users[userIndex].profileImg
    };

    localStorage.setItem(USERS_KEY, JSON.stringify(users));

    // If email updated, generate a new token
    const newToken = newEmail.toLowerCase() !== originalEmail.toLowerCase() 
      ? `mock-jwt-token-${btoa(newEmail)}` 
      : token;

    const { password: _, ...userProfile } = users[userIndex];
    return { user: userProfile, token: newToken };
  },

  getCurrentUser: async (token) => {
    await delay(200); // Shorter delay for initial session check
    if (!token) return null;

    const emailBase64 = token.replace('mock-jwt-token-', '');
    let email;
    try {
      email = atob(emailBase64);
    } catch {
      return null;
    }

    const users = getStoredUsers();
    const user = users.find(u => u.email.toLowerCase() === email.toLowerCase());
    if (!user) return null;

    const { password: _, ...userProfile } = user;
    return userProfile;
  }
};
