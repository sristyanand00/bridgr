import { auth } from '../config/firebase';

export const getCurrentUserToken = async () => {
  const user = auth.currentUser;
  
  if (user) {
    try {
      const token = await user.getIdToken();
      return token;
    } catch (error) {
      console.error('Error getting auth token:', error);
      return null;
    }
  }
  
  return null;
};

export const getCurrentUser = () => {
  return auth.currentUser;
};
