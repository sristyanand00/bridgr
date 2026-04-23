export const QUIZ_QUESTIONS = [
  {
    id: "stage",
    q: "Where are you in your career right now?",
    sub: "This shapes everything — your roadmap, advice, and salary context.",
    opts: ["Student", "Fresh graduate", "Working — switching roles", "Working — leveling up", "Career break", "Freelancer"]
  },
  {
    id: "timeline",
    q: "What's your timeline?",
    sub: "This is the most important context for your AI coach.",
    opts: ["Interview in the next month", "3–6 months", "6–12 months", "Exploring, no rush"]
  },
  {
    id: "blocker",
    q: "What's your biggest blocker right now?",
    sub: "Two people with identical resumes can need completely different help.",
    opts: ["I don't know what skills I'm missing", "I know what to learn but not how", "I lack confidence for interviews", "I'm applying but getting no responses", "I don't know which role is right for me"]
  },
  {
    id: "hours",
    q: "How much time can you commit per week?",
    sub: "Your roadmap timeline adjusts to this — we keep it realistic.",
    opts: ["Less than 3 hours", "3–7 hours", "7–15 hours", "15+ hours"]
  },
  {
    id: "city",
    q: "Which city are you based in?",
    sub: "Salary bands and job market signals are city-specific.",
    opts: ["Bengaluru", "Mumbai", "Delhi / NCR", "Hyderabad", "Pune", "Remote", "Other city"]
  },
  {
    id: "applied",
    q: "Have you applied to jobs for this role before?",
    sub: "This tells us where the actual problem is.",
    opts: ["No, still preparing", "Applied but no responses", "Got interviews but no offers", "I have an offer and want to prepare"]
  },
  {
    id: "currentRole",
    q: "What's your current role or field?",
    sub: "Optional — helps us spot transferable skills you might be underselling.",
    freeText: true,
    placeholder: "e.g. Marketing Analyst, CS Student, Software Engineer…",
    optional: true
  }
];
