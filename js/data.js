// Mock data for challenges
const challenges = [
    {
        id: 1,
        role: 'Sales Representative',
        prompt: 'Sell me this smartphone in 30 seconds. Focus on the key benefits that would matter most to a potential customer.',
        duration: 30,
        difficulty: 'Easy',
        icon: '📱'
    },
    {
        id: 2,
        role: 'Customer Support',
        prompt: 'A customer wants a refund for a product they bought 6 months ago, but our policy only allows 30-day returns. How would you handle this situation?',
        duration: 45,
        difficulty: 'Medium',
        icon: '🎧'
    },
    {
        id: 3,
        role: 'Tech Support',
        prompt: 'Walk me through how you would help a non-technical user reset their home WiFi router over the phone.',
        duration: 60,
        difficulty: 'Medium',
        icon: '🔧'
    },
    {
        id: 4,
        role: 'Teacher',
        prompt: 'Explain Newton\'s First Law of Motion to a 6th-grade student using simple examples they can understand.',
        duration: 45,
        difficulty: 'Easy',
        icon: '📚'
    }
];

// Mock data for candidates
const mockCandidates = [
    {
        id: 1,
        name: 'Priya Sharma',
        email: 'priya.sharma@email.com',
        role: 'Sales Representative',
        overallScore: 8.7,
        fluency: 9.2,
        confidence: 8.5,
        relevance: 8.4,
        clarity: 8.8,
        duration: '28s',
        submittedAt: '2 hours ago',
        status: 'completed'
    },
    {
        id: 2,
        name: 'Rahul Gupta',
        email: 'rahul.gupta@email.com',
        role: 'Customer Support',
        overallScore: 7.9,
        fluency: 8.1,
        confidence: 7.8,
        relevance: 8.2,
        clarity: 7.5,
        duration: '42s',
        submittedAt: '5 hours ago',
        status: 'completed'
    },
    {
        id: 3,
        name: 'Anjali Reddy',
        email: 'anjali.reddy@email.com',
        role: 'Tech Support',
        overallScore: 9.1,
        fluency: 9.0,
        confidence: 9.3,
        relevance: 9.2,
        clarity: 9.0,
        duration: '58s',
        submittedAt: '1 day ago',
        status: 'completed'
    },
    {
        id: 4,
        name: 'Vikram Singh',
        email: 'vikram.singh@email.com',
        role: 'Teacher',
        overallScore: 8.3,
        fluency: 8.7,
        confidence: 8.0,
        relevance: 8.5,
        clarity: 8.0,
        duration: '44s',
        submittedAt: '1 day ago',
        status: 'completed'
    },
    {
        id: 5,
        name: 'Neha Patel',
        email: 'neha.patel@email.com',
        role: 'Sales Representative',
        overallScore: 9.2,
        fluency: 9.5,
        confidence: 9.0,
        relevance: 9.1,
        clarity: 9.2,
        duration: '29s',
        submittedAt: '3 hours ago',
        status: 'completed'
    },
    {
        id: 6,
        name: 'Arjun Kumar',
        email: 'arjun.kumar@email.com',
        role: 'Customer Support',
        overallScore: 7.5,
        fluency: 7.8,
        confidence: 7.2,
        relevance: 7.6,
        clarity: 7.4,
        duration: '46s',
        submittedAt: '1 day ago',
        status: 'completed'
    }
];

// Sample challenge history for candidate dashboard
const sampleChallengeHistory = [
    {
        role: 'Sales Representative',
        submittedAt: '2 hours ago',
        overallScore: 8.7,
        fluency: 9.2,
        confidence: 8.5,
        relevance: 8.4,
        clarity: 8.8
    },
    {
        role: 'Customer Support',
        submittedAt: '1 day ago',
        overallScore: 8.3,
        fluency: 8.5,
        confidence: 8.0,
        relevance: 8.4,
        clarity: 8.3
    }
]; 