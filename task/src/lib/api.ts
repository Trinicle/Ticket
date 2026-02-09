// Example API service using native fetch
// You can replace this with Axios once you install it

const API_BASE_URL = 'https://jsonplaceholder.typicode.com';

export interface Post {
  id: number;
  title: string;
  body: string;
  userId: number;
}

export interface User {
  id: number;
  name: string;
  email: string;
  username: string;
}

export interface Comment {
  id: number;
  name: string;
  email: string;
  body: string;
  postId: number;
}

// API functions using fetch (replace with Axios if preferred)
export const api = {
  // GET requests
  async getPosts(limit = 10): Promise<Post[]> {
    const response = await fetch(`${API_BASE_URL}/posts?_limit=${limit}`);
    if (!response.ok)
      throw new Error(`Failed to fetch posts: ${response.status}`);
    return response.json();
  },

  async getUsers(limit = 10): Promise<User[]> {
    const response = await fetch(`${API_BASE_URL}/users?_limit=${limit}`);
    if (!response.ok)
      throw new Error(`Failed to fetch users: ${response.status}`);
    return response.json();
  },

  async getComments(limit = 10): Promise<Comment[]> {
    const response = await fetch(`${API_BASE_URL}/comments?_limit=${limit}`);
    if (!response.ok)
      throw new Error(`Failed to fetch comments: ${response.status}`);
    return response.json();
  },

  // POST request example
  async createPost(post: Omit<Post, 'id'>): Promise<Post> {
    const response = await fetch(`${API_BASE_URL}/posts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(post),
    });
    if (!response.ok)
      throw new Error(`Failed to create post: ${response.status}`);
    return response.json();
  },
};

// Axios version (uncomment after installing axios):
/*
import axios from 'axios';

const axiosApi = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

export const axiosAPI = {
  async getPosts(limit = 10): Promise<Post[]> {
    const response = await axiosApi.get(`/posts?_limit=${limit}`);
    return response.data;
  },

  async getUsers(limit = 10): Promise<User[]> {
    const response = await axiosApi.get(`/users?_limit=${limit}`);
    return response.data;
  },

  async getComments(limit = 10): Promise<Comment[]> {
    const response = await axiosApi.get(`/comments?_limit=${limit}`);
    return response.data;
  },

  async createPost(post: Omit<Post, 'id'>): Promise<Post> {
    const response = await axiosApi.post('/posts', post);
    return response.data;
  },
};
*/
