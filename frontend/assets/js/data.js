// Mock data for challenges
const challenges = [
    // Existing Non-Tech Roles
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
    },
    
    // Software Developer Roles by Language
    {
        id: 5,
        role: 'JavaScript Developer',
        prompt: 'Explain how you would optimize a slow-loading React component in a production application. Walk through your debugging process and solution approach.',
        duration: 60,
        difficulty: 'Medium',
        icon: '🟨'
    },
    {
        id: 6,
        role: 'Python Developer',
        prompt: 'Describe how you would design a REST API for a user management system using Python. Include authentication, data validation, and error handling.',
        duration: 75,
        difficulty: 'Hard',
        icon: '🐍'
    },
    {
        id: 7,
        role: 'Java Developer',
        prompt: 'Explain the difference between ArrayList and LinkedList in Java, and when you would use each one in a real-world application.',
        duration: 50,
        difficulty: 'Medium',
        icon: '☕'
    },
    {
        id: 8,
        role: 'C++ Developer',
        prompt: 'Walk through how you would implement a memory-efficient solution for handling large datasets in C++. Discuss memory management and optimization strategies.',
        duration: 70,
        difficulty: 'Hard',
        icon: '⚡'
    },
    {
        id: 9,
        role: 'C# Developer',
        prompt: 'Explain how you would implement dependency injection in a .NET Core application and why it\'s important for maintainable code.',
        duration: 60,
        difficulty: 'Medium',
        icon: '🔷'
    },
    {
        id: 10,
        role: 'PHP Developer',
        prompt: 'Describe how you would secure a PHP web application against common vulnerabilities like SQL injection and XSS attacks.',
        duration: 65,
        difficulty: 'Medium',
        icon: '🐘'
    },
    {
        id: 11,
        role: 'Ruby Developer',
        prompt: 'Explain how Rails conventions help with rapid development and walk through creating a simple CRUD API with authentication.',
        duration: 70,
        difficulty: 'Medium',
        icon: '💎'
    },
    {
        id: 12,
        role: 'Go Developer',
        prompt: 'Describe Go\'s concurrency model with goroutines and channels. Provide an example of when you\'d use this in a microservices architecture.',
        duration: 65,
        difficulty: 'Hard',
        icon: '🔵'
    },
    {
        id: 13,
        role: 'Swift Developer',
        prompt: 'Explain how you would optimize an iOS app for better performance and user experience. Discuss memory management and UI responsiveness.',
        duration: 60,
        difficulty: 'Medium',
        icon: '🦉'
    },
    {
        id: 14,
        role: 'Kotlin Developer',
        prompt: 'Describe the benefits of Kotlin over Java for Android development and walk through implementing a modern Android architecture pattern.',
        duration: 65,
        difficulty: 'Medium',
        icon: '🤖'
    },
    {
        id: 15,
        role: 'Rust Developer',
        prompt: 'Explain Rust\'s ownership system and how it prevents memory safety issues. Provide an example of when Rust would be preferred over other languages.',
        duration: 70,
        difficulty: 'Hard',
        icon: '🦀'
    },
    {
        id: 16,
        role: 'TypeScript Developer',
        prompt: 'Describe how TypeScript improves JavaScript development and walk through implementing type-safe API calls with proper error handling.',
        duration: 55,
        difficulty: 'Medium',
        icon: '🔷'
    },
    
    // Additional Software Engineering Roles
    {
        id: 17,
        role: 'Full Stack Developer',
        prompt: 'Explain how you would architect a scalable web application from database to frontend. Discuss technology choices and system design considerations.',
        duration: 80,
        difficulty: 'Hard',
        icon: '🌐'
    },
    {
        id: 18,
        role: 'DevOps Engineer',
        prompt: 'Walk through setting up a CI/CD pipeline for a web application. Include testing, deployment strategies, and monitoring considerations.',
        duration: 75,
        difficulty: 'Hard',
        icon: '⚙️'
    },
    {
        id: 19,
        role: 'Mobile Developer',
        prompt: 'Compare native vs cross-platform mobile development approaches. Explain when you would choose React Native, Flutter, or native development.',
        duration: 60,
        difficulty: 'Medium',
        icon: '📱'
    },
    {
        id: 20,
        role: 'Data Engineer',
        prompt: 'Describe how you would design a data pipeline to process large volumes of user analytics data. Include data validation and real-time processing.',
        duration: 70,
        difficulty: 'Hard',
        icon: '📊'
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
    },
    // Software Developer Candidates
    {
        id: 7,
        name: 'Ravi Krishnan',
        email: 'ravi.krishnan@email.com',
        role: 'JavaScript Developer',
        overallScore: 9.3,
        fluency: 9.1,
        confidence: 9.4,
        relevance: 9.5,
        clarity: 9.2,
        duration: '58s',
        submittedAt: '3 hours ago',
        status: 'completed'
    },
    {
        id: 8,
        name: 'Sneha Agarwal',
        email: 'sneha.agarwal@email.com',
        role: 'Python Developer',
        overallScore: 8.9,
        fluency: 8.7,
        confidence: 9.1,
        relevance: 9.0,
        clarity: 8.8,
        duration: '72s',
        submittedAt: '6 hours ago',
        status: 'completed'
    },
    {
        id: 9,
        name: 'Karthik Raj',
        email: 'karthik.raj@email.com',
        role: 'Java Developer',
        overallScore: 8.6,
        fluency: 8.8,
        confidence: 8.3,
        relevance: 8.7,
        clarity: 8.6,
        duration: '48s',
        submittedAt: '12 hours ago',
        status: 'completed'
    },
    {
        id: 10,
        name: 'Deepika Nair',
        email: 'deepika.nair@email.com',
        role: 'Full Stack Developer',
        overallScore: 9.0,
        fluency: 9.2,
        confidence: 8.9,
        relevance: 9.1,
        clarity: 8.8,
        duration: '76s',
        submittedAt: '8 hours ago',
        status: 'completed'
    },
    {
        id: 11,
        name: 'Amit Verma',
        email: 'amit.verma@email.com',
        role: 'DevOps Engineer',
        overallScore: 8.7,
        fluency: 8.5,
        confidence: 8.8,
        relevance: 8.9,
        clarity: 8.6,
        duration: '70s',
        submittedAt: '1 day ago',
        status: 'completed'
    },
    {
        id: 12,
        name: 'Pooja Singh',
        email: 'pooja.singh@email.com',
        role: 'React Developer',
        overallScore: 8.8,
        fluency: 9.0,
        confidence: 8.7,
        relevance: 8.9,
        clarity: 8.6,
        duration: '62s',
        submittedAt: '4 hours ago',
        status: 'completed'
    },
    {
        id: 13,
        name: 'Rohit Sharma',
        email: 'rohit.sharma@email.com',
        role: 'C++ Developer',
        overallScore: 8.4,
        fluency: 8.2,
        confidence: 8.5,
        relevance: 8.6,
        clarity: 8.3,
        duration: '68s',
        submittedAt: '2 days ago',
        status: 'completed'
    },
    {
        id: 14,
        name: 'Kavya Menon',
        email: 'kavya.menon@email.com',
        role: 'Swift Developer',
        overallScore: 9.1,
        fluency: 9.3,
        confidence: 8.9,
        relevance: 9.2,
        clarity: 9.0,
        duration: '59s',
        submittedAt: '5 hours ago',
        status: 'completed'
    }
];

// Sample challenge history for candidate dashboard
const sampleChallengeHistory = [
    {
        role: 'JavaScript Developer',
        submittedAt: '2 hours ago',
        overallScore: 9.1,
        fluency: 9.3,
        confidence: 8.9,
        relevance: 9.2,
        clarity: 9.0
    },
    {
        role: 'Python Developer',
        submittedAt: '1 day ago',
        overallScore: 8.8,
        fluency: 8.6,
        confidence: 9.0,
        relevance: 8.9,
        clarity: 8.7
    },
    {
        role: 'Full Stack Developer',
        submittedAt: '3 days ago',
        overallScore: 8.5,
        fluency: 8.7,
        confidence: 8.3,
        relevance: 8.6,
        clarity: 8.4
    }
]; 