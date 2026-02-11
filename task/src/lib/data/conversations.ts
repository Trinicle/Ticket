export interface Conversation {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: Date;
  messageCount: number;
}

export interface ChatMessage {
  id: string;
  from: 'user' | 'model';
  content: string;
  timestamp: Date;
  status?: 'sending' | 'processing' | 'complete' | 'error';
}

// Generate mock conversations with varied timestamps
const now = Date.now();
const thirtyMinutesAgo = new Date(now - 1000 * 60 * 30);
const twoHoursAgo = new Date(now - 1000 * 60 * 60 * 2);
const yesterday = new Date(now - 1000 * 60 * 60 * 24);
const threeDaysAgo = new Date(now - 1000 * 60 * 60 * 24 * 3);
const lastWeek = new Date(now - 1000 * 60 * 60 * 24 * 7);

export const mockConversations: Conversation[] = [
  {
    id: 'conv-1',
    title: 'GitHub Issue Analysis',
    lastMessage: 'I found 3 open issues related to authentication...',
    timestamp: thirtyMinutesAgo,
    messageCount: 4
  },
  {
    id: 'conv-2',
    title: 'Repository Statistics',
    lastMessage: 'The repository has 45 open issues and 12 pull requests.',
    timestamp: twoHoursAgo,
    messageCount: 6
  },
  {
    id: 'conv-3',
    title: 'Team Velocity Metrics',
    lastMessage: 'Based on the data, your team closed 23 issues this week.',
    timestamp: yesterday,
    messageCount: 5
  },
  {
    id: 'conv-4',
    title: 'Codebase Query',
    lastMessage: 'The authentication module is located in src/auth/',
    timestamp: threeDaysAgo,
    messageCount: 3
  },
  {
    id: 'conv-5',
    title: 'Issue Creation Help',
    lastMessage: 'I can help you create a new issue. What would you like to track?',
    timestamp: lastWeek,
    messageCount: 7
  },
  {
    id: 'conv-6',
    title: 'Label Management',
    lastMessage: 'All labels have been updated successfully.',
    timestamp: new Date(now - 1000 * 60 * 15), // 15 minutes ago
    messageCount: 4
  },
  {
    id: 'conv-7',
    title: 'Pull Request Review',
    lastMessage: 'The PR #42 has been reviewed and approved.',
    timestamp: new Date(now - 1000 * 60 * 45), // 45 minutes ago
    messageCount: 8
  }
];

export const mockMessages: Record<string, ChatMessage[]> = {
  'conv-1': [
    {
      id: 'msg-1-1',
      from: 'user',
      content: 'Can you analyze the open issues in the repository?',
      timestamp: new Date(thirtyMinutesAgo.getTime() - 1000 * 60 * 10),
      status: 'complete'
    },
    {
      id: 'msg-1-2',
      from: 'model',
      content: 'I\'ll analyze the open issues for you. Let me fetch the data...',
      timestamp: new Date(thirtyMinutesAgo.getTime() - 1000 * 60 * 9),
      status: 'complete'
    },
    {
      id: 'msg-1-3',
      from: 'user',
      content: 'Focus on authentication-related issues',
      timestamp: new Date(thirtyMinutesAgo.getTime() - 1000 * 60 * 5),
      status: 'complete'
    },
    {
      id: 'msg-1-4',
      from: 'model',
      content: 'I found 3 open issues related to authentication:\n\n1. Issue #42: "OAuth token refresh failing"\n2. Issue #58: "Session timeout too short"\n3. Issue #71: "Password reset email not sending"\n\nWould you like me to get more details on any of these?',
      timestamp: thirtyMinutesAgo,
      status: 'complete'
    }
  ],
  'conv-2': [
    {
      id: 'msg-2-1',
      from: 'user',
      content: 'Show me repository statistics',
      timestamp: new Date(twoHoursAgo.getTime() - 1000 * 60 * 20),
      status: 'complete'
    },
    {
      id: 'msg-2-2',
      from: 'model',
      content: 'Fetching repository statistics...',
      timestamp: new Date(twoHoursAgo.getTime() - 1000 * 60 * 19),
      status: 'complete'
    },
    {
      id: 'msg-2-3',
      from: 'model',
      content: 'Here are the current repository statistics:\n\n- Open Issues: 45\n- Closed Issues: 234\n- Open Pull Requests: 12\n- Merged Pull Requests: 189\n- Contributors: 28\n- Stars: 1,234',
      timestamp: new Date(twoHoursAgo.getTime() - 1000 * 60 * 18),
      status: 'complete'
    },
    {
      id: 'msg-2-4',
      from: 'user',
      content: 'What about the last 30 days?',
      timestamp: new Date(twoHoursAgo.getTime() - 1000 * 60 * 10),
      status: 'complete'
    },
    {
      id: 'msg-2-5',
      from: 'model',
      content: 'In the last 30 days:\n\n- 12 new issues opened\n- 18 issues closed\n- 5 new pull requests\n- 8 pull requests merged',
      timestamp: new Date(twoHoursAgo.getTime() - 1000 * 60 * 9),
      status: 'complete'
    },
    {
      id: 'msg-2-6',
      from: 'model',
      content: 'The repository has 45 open issues and 12 pull requests.',
      timestamp: twoHoursAgo,
      status: 'complete'
    }
  ],
  'conv-3': [
    {
      id: 'msg-3-1',
      from: 'user',
      content: 'What\'s our team velocity this week?',
      timestamp: new Date(yesterday.getTime() - 1000 * 60 * 30),
      status: 'complete'
    },
    {
      id: 'msg-3-2',
      from: 'model',
      content: 'Calculating team velocity metrics...',
      timestamp: new Date(yesterday.getTime() - 1000 * 60 * 29),
      status: 'complete'
    },
    {
      id: 'msg-3-3',
      from: 'model',
      content: 'Based on the data, your team closed 23 issues this week.',
      timestamp: yesterday,
      status: 'complete'
    },
    {
      id: 'msg-3-4',
      from: 'user',
      content: 'Compare to last week',
      timestamp: new Date(yesterday.getTime() - 1000 * 60 * 5),
      status: 'complete'
    },
    {
      id: 'msg-3-5',
      from: 'model',
      content: 'Last week your team closed 19 issues, so this week shows a 21% increase in velocity.',
      timestamp: new Date(yesterday.getTime() - 1000 * 60 * 4),
      status: 'complete'
    }
  ],
  'conv-4': [
    {
      id: 'msg-4-1',
      from: 'user',
      content: 'Where is the authentication code located?',
      timestamp: new Date(threeDaysAgo.getTime() - 1000 * 60 * 15),
      status: 'complete'
    },
    {
      id: 'msg-4-2',
      from: 'model',
      content: 'Searching the codebase for authentication-related files...',
      timestamp: new Date(threeDaysAgo.getTime() - 1000 * 60 * 14),
      status: 'complete'
    },
    {
      id: 'msg-4-3',
      from: 'model',
      content: 'The authentication module is located in src/auth/',
      timestamp: threeDaysAgo,
      status: 'complete'
    }
  ],
  'conv-5': [
    {
      id: 'msg-5-1',
      from: 'user',
      content: 'I need to create a new issue',
      timestamp: new Date(lastWeek.getTime() - 1000 * 60 * 45),
      status: 'complete'
    },
    {
      id: 'msg-5-2',
      from: 'model',
      content: 'I can help you create a new issue. What would you like to track?',
      timestamp: lastWeek,
      status: 'complete'
    },
    {
      id: 'msg-5-3',
      from: 'user',
      content: 'A bug in the login flow',
      timestamp: new Date(lastWeek.getTime() - 1000 * 60 * 40),
      status: 'complete'
    },
    {
      id: 'msg-5-4',
      from: 'model',
      content: 'I can create an issue for the login flow bug. Would you like me to:\n\n1. Create it now with a default title and description?\n2. Let you provide more details first?\n\nWhat would you prefer?',
      timestamp: new Date(lastWeek.getTime() - 1000 * 60 * 39),
      status: 'complete'
    },
    {
      id: 'msg-5-5',
      from: 'user',
      content: 'Let me provide more details',
      timestamp: new Date(lastWeek.getTime() - 1000 * 60 * 35),
      status: 'complete'
    },
    {
      id: 'msg-5-6',
      from: 'model',
      content: 'Please provide:\n- Title for the issue\n- Description of the bug\n- Steps to reproduce (if known)\n- Expected vs actual behavior',
      timestamp: new Date(lastWeek.getTime() - 1000 * 60 * 34),
      status: 'complete'
    },
    {
      id: 'msg-5-7',
      from: 'user',
      content: 'Title: Login fails with OAuth providers\nDescription: Users cannot log in using Google or GitHub OAuth',
      timestamp: new Date(lastWeek.getTime() - 1000 * 60 * 30),
      status: 'complete'
    }
  ],
  'conv-6': [
    {
      id: 'msg-6-1',
      from: 'user',
      content: 'Update all bug labels to use "bug" instead of "Bug"',
      timestamp: new Date(now - 1000 * 60 * 20),
      status: 'complete'
    },
    {
      id: 'msg-6-2',
      from: 'model',
      content: 'I\'ll update the label naming convention for you.',
      timestamp: new Date(now - 1000 * 60 * 19),
      status: 'complete'
    },
    {
      id: 'msg-6-3',
      from: 'model',
      content: 'All labels have been updated successfully.',
      timestamp: new Date(now - 1000 * 60 * 15),
      status: 'complete'
    },
    {
      id: 'msg-6-4',
      from: 'user',
      content: 'Thanks!',
      timestamp: new Date(now - 1000 * 60 * 14),
      status: 'complete'
    }
  ],
  'conv-7': [
    {
      id: 'msg-7-1',
      from: 'user',
      content: 'Review pull request #42',
      timestamp: new Date(now - 1000 * 60 * 50),
      status: 'complete'
    },
    {
      id: 'msg-7-2',
      from: 'model',
      content: 'Analyzing pull request #42...',
      timestamp: new Date(now - 1000 * 60 * 49),
      status: 'complete'
    },
    {
      id: 'msg-7-3',
      from: 'model',
      content: 'PR #42 Summary:\n- Title: "Add dark mode support"\n- Author: @johndoe\n- Files changed: 12\n- Additions: +234 lines\n- Deletions: -45 lines\n- Status: Open',
      timestamp: new Date(now - 1000 * 60 * 48),
      status: 'complete'
    },
    {
      id: 'msg-7-4',
      from: 'user',
      content: 'What are the main changes?',
      timestamp: new Date(now - 1000 * 60 * 47),
      status: 'complete'
    },
    {
      id: 'msg-7-5',
      from: 'model',
      content: 'The main changes include:\n1. Added dark mode theme configuration\n2. Updated CSS variables for color schemes\n3. Added theme toggle component\n4. Updated all components to support dark mode',
      timestamp: new Date(now - 1000 * 60 * 46),
      status: 'complete'
    },
    {
      id: 'msg-7-6',
      from: 'user',
      content: 'Approve it',
      timestamp: new Date(now - 1000 * 60 * 45),
      status: 'complete'
    },
    {
      id: 'msg-7-7',
      from: 'model',
      content: 'The PR #42 has been reviewed and approved.',
      timestamp: new Date(now - 1000 * 60 * 45),
      status: 'complete'
    },
    {
      id: 'msg-7-8',
      from: 'user',
      content: 'Great!',
      timestamp: new Date(now - 1000 * 60 * 44),
      status: 'complete'
    }
  ]
};

// Helper function to format timestamp for display
export function formatTimestamp(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  
  return date.toLocaleDateString();
}

// Helper function to generate a new conversation ID
export function generateConversationId(): string {
  return `conv-${Date.now()}`;
}

// Helper function to generate a new message ID
export function generateMessageId(): string {
  return `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}
