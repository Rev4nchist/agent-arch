# AI Guide Persona-Based Testing Framework

## Overview
This document defines 7 user personas that represent key stakeholders who will interact with the Agent Architecture Platform's AI Guide. Each persona has distinct use cases, query patterns, and success criteria.

---

## Persona Profiles

### 1. DEVELOPER (Michael Roberts)
**Role:** Full-Stack Developer
**Department:** Engineering
**Primary Goals:**
- Track assigned tasks and deadlines
- Find technical documentation and patterns
- Understand agent development requirements
- Check meeting action items assigned to him

**Typical Query Patterns:**
- Task-focused: "what tasks are assigned to me?", "show my overdue tasks"
- Technical: "what code patterns are available?", "find tasks about API"
- Status: "what's blocking development?", "show in-progress tasks"
- Context: Usually on /tasks or /architecture pages

**Expected AI Guide Behaviors:**
- Prioritize technical tasks and code-related results
- Suggest action items like "Filter by assignee" or "View blocked tasks"
- Provide technical details in responses
- Reference related technical documentation

---

### 2. ARCHITECT (Sarah Chen)
**Role:** Solutions Architect
**Department:** Architecture
**Primary Goals:**
- Review system design decisions
- Track architectural proposals
- Monitor agent tier classifications
- Oversee technical governance

**Typical Query Patterns:**
- Architecture: "show all Tier 2 agents", "what agents are in development?"
- Decisions: "list recent architecture decisions", "what proposals are pending?"
- Governance: "explain agent tier requirements", "what is the approval process?"
- Patterns: "find code-first patterns", "show deployment guides"

**Expected AI Guide Behaviors:**
- Emphasize architectural context and decisions
- Suggest reviewing proposals or tech radar items
- Provide tier classification details
- Reference governance policies

---

### 3. AI ENABLEMENT DIRECTOR (Emma Wilson)
**Role:** AI Enablement Director
**Department:** AI Center of Excellence
**Primary Goals:**
- Track AI agent portfolio
- Monitor adoption metrics
- Oversee governance compliance
- Drive AI strategy execution

**Typical Query Patterns:**
- Portfolio: "how many agents by status?", "breakdown agents by tier"
- Strategic: "what agents are in production?", "show agent pipeline"
- Metrics: "how many tasks completed this week?", "meeting activity summary"
- Governance: "any compliance issues?", "pending proposals needing review"

**Expected AI Guide Behaviors:**
- Provide executive summaries with aggregations
- Highlight portfolio health metrics
- Surface compliance and governance items
- Suggest strategic actions

---

### 4. CTO (James Anderson)
**Role:** Chief Technology Officer
**Department:** Executive
**Primary Goals:**
- High-level technology overview
- Strategic decision tracking
- Budget and resource visibility
- Risk and compliance awareness

**Typical Query Patterns:**
- Executive: "executive summary of agents", "technology portfolio overview"
- Decisions: "what major decisions were made this month?"
- Resources: "azure resource status", "budget utilization"
- Risk: "any blocked initiatives?", "security concerns?"

**Expected AI Guide Behaviors:**
- Provide concise executive summaries
- Aggregate data into high-level metrics
- Highlight critical issues requiring attention
- Avoid technical jargon, focus on business impact

---

### 5. BIZOPS VP (Jennifer Martinez)
**Role:** VP of Business Operations
**Department:** Operations
**Primary Goals:**
- Track operational metrics
- Monitor team productivity
- Ensure process compliance
- Resource allocation visibility

**Typical Query Patterns:**
- Metrics: "team productivity this week", "task completion rate"
- Workload: "workload distribution by assignee", "who is overloaded?"
- Meetings: "upcoming governance meetings", "action item completion"
- Process: "pending approvals", "overdue items"

**Expected AI Guide Behaviors:**
- Focus on operational metrics and trends
- Provide workload distribution insights
- Highlight process bottlenecks
- Suggest workflow improvements

---

### 6. IT PERSONNEL (David Hayes)
**Role:** IT Platform Administrator
**Department:** IT Operations
**Primary Goals:**
- Monitor infrastructure health
- Track Azure resource deployments
- Ensure platform availability
- Support development teams

**Typical Query Patterns:**
- Infrastructure: "azure resource status", "what services are deployed?"
- Support: "any integration issues?", "blocked deployments?"
- Operations: "recent system changes", "infrastructure tasks"
- Technical: "CosmosDB status", "search index health"

**Expected AI Guide Behaviors:**
- Provide infrastructure-focused responses
- Surface Azure resource information
- Highlight operational concerns
- Suggest infrastructure-related actions

---

### 7. SECURITY TEAM (Emma Wilson - Security Hat)
**Role:** Security Analyst
**Department:** Information Security
**Primary Goals:**
- Review security-related decisions
- Audit access patterns
- Monitor compliance requirements
- Track security-related tasks

**Typical Query Patterns:**
- Security: "security-related decisions", "compliance tasks"
- Audit: "who accessed what?", "recent changes to security settings"
- Compliance: "governance policies", "approval workflows"
- Risk: "blocked security items", "critical priority tasks"

**Expected AI Guide Behaviors:**
- Prioritize security and compliance content
- Reference governance policies
- Highlight audit-relevant information
- Suggest security review actions

---

## Test Scenarios Per Persona

### Developer Tests
| ID | Query | Expected Intent | Success Criteria |
|----|-------|-----------------|------------------|
| DEV-01 | "show my tasks" | LIST | Returns task list with assignee context |
| DEV-02 | "what tasks are in progress?" | STATUS_CHECK | Returns in-progress tasks only |
| DEV-03 | "find tasks about search" | SEARCH | Returns tasks with 'search' in title/desc |
| DEV-04 | "what's blocking development?" | STATUS_CHECK | Returns blocked tasks with blockers |
| DEV-05 | "show high priority tasks assigned to David" | LIST + FILTER | Returns filtered results |

### Architect Tests
| ID | Query | Expected Intent | Success Criteria |
|----|-------|-----------------|------------------|
| ARCH-01 | "list all agents by tier" | AGGREGATION | Returns agent tier breakdown |
| ARCH-02 | "show agents in development" | LIST + FILTER | Returns development-status agents |
| ARCH-03 | "what proposals are pending review?" | LIST + FILTER | Returns pending proposals |
| ARCH-04 | "explain the agent tier system" | EXPLANATION | Returns governance explanation |
| ARCH-05 | "recent architecture decisions" | LIST | Returns decision list |

### AI Director Tests
| ID | Query | Expected Intent | Success Criteria |
|----|-------|-----------------|------------------|
| AID-01 | "breakdown agents by status" | AGGREGATION | Returns status distribution |
| AID-02 | "how many tasks completed this week?" | AGGREGATION | Returns week's completion count |
| AID-03 | "agent portfolio summary" | AGGREGATION | Returns multi-metric summary |
| AID-04 | "pending governance items" | LIST | Returns pending proposals/decisions |
| AID-05 | "what's the adoption trend?" | AGGREGATION | Returns trend data if available |

### CTO Tests
| ID | Query | Expected Intent | Success Criteria |
|----|-------|-----------------|------------------|
| CTO-01 | "executive summary" | AGGREGATION | Returns high-level overview |
| CTO-02 | "what are the critical blockers?" | STATUS_CHECK | Returns critical/blocked items |
| CTO-03 | "technology portfolio status" | AGGREGATION | Returns agent/tech summary |
| CTO-04 | "major decisions this month" | LIST | Returns recent decisions |
| CTO-05 | "any security or compliance concerns?" | SEARCH | Returns relevant items |

### BizOps VP Tests
| ID | Query | Expected Intent | Success Criteria |
|----|-------|-----------------|------------------|
| BIZ-01 | "workload by assignee" | AGGREGATION | Returns assignee distribution |
| BIZ-02 | "overdue tasks" | STATUS_CHECK | Returns overdue items |
| BIZ-03 | "meeting completion rate" | AGGREGATION | Returns meeting metrics |
| BIZ-04 | "pending approvals" | LIST | Returns items needing approval |
| BIZ-05 | "team productivity this week" | AGGREGATION | Returns productivity metrics |

### IT Personnel Tests
| ID | Query | Expected Intent | Success Criteria |
|----|-------|-----------------|------------------|
| IT-01 | "infrastructure tasks" | SEARCH | Returns infra-related tasks |
| IT-02 | "blocked deployments" | STATUS_CHECK | Returns blocked deployment tasks |
| IT-03 | "azure resources" | LIST | Returns resource information |
| IT-04 | "recent system changes" | LIST | Returns recent updates |
| IT-05 | "integration issues" | SEARCH | Returns integration problems |

### Security Tests
| ID | Query | Expected Intent | Success Criteria |
|----|-------|-----------------|------------------|
| SEC-01 | "security decisions" | SEARCH | Returns security-related decisions |
| SEC-02 | "compliance tasks" | SEARCH | Returns compliance items |
| SEC-03 | "governance policies" | EXPLANATION | Returns policy information |
| SEC-04 | "critical security items" | STATUS_CHECK | Returns critical priority items |
| SEC-05 | "audit trail" | LIST | Returns recent activity |

---

## Success Metrics

### Per-Persona Metrics
- Query accuracy rate (correct intent classification)
- Response relevance score (1-5)
- Action suggestion appropriateness
- Response time (<2s target)

### Overall Platform Metrics
- Total tests passed / total tests
- Intent classification accuracy by type
- Aggregation query correctness
- Filter application accuracy

---

## Report Template

```
=== AI GUIDE PERSONA TEST REPORT ===
Generated: [timestamp]

EXECUTIVE SUMMARY
-----------------
Total Personas Tested: 7
Total Test Cases: 35
Overall Pass Rate: XX%

PER-PERSONA RESULTS
-------------------
[Persona Name]: X/5 passed (XX%)
  - Strengths: [observations]
  - Issues: [if any]
  - Recommendations: [improvements]

FEATURE COVERAGE
----------------
Intent Classification: XX%
Query Filters: XX%
Aggregations: XX%
Search: XX%
Suggestions: XX%

ISSUES FOUND
------------
[List of specific issues]

RECOMMENDATIONS
---------------
[Prioritized improvement suggestions]
```
