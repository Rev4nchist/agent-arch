# Deployment Notes

## Feature Updates - Initial Data Population

When deploying to production, populate the Feature Updates page with the following entries via POST to `/api/feature-updates`:

### 1. Welcome to Feature Updates!
```json
{
  "title": "Welcome to Feature Updates!",
  "description": "This is where you'll find all the latest improvements, new features, and fixes to the Fourth AI Architecture platform. We'll keep you informed about what's new in a clear, non-technical way.",
  "category": "Announcement",
  "related_pages": ["/updates"],
  "created_by": "Platform Team",
  "published_at": "2024-12-09T10:00:00Z"
}
```

### 2. AI Guide Now Remembers Your Preferences
```json
{
  "title": "AI Guide Now Remembers Your Preferences",
  "description": "The AI Guide now uses a memory system to remember your preferences, past conversations, and context. This means more personalized and relevant assistance every time you use it.",
  "category": "New Feature",
  "related_pages": ["/guide", "/memories"],
  "created_by": "Platform Team",
  "published_at": "2024-12-08T14:00:00Z"
}
```

### 3. Smarter Action Chips in AI Guide
```json
{
  "title": "Smarter Action Chips in AI Guide",
  "description": "The AI Guide now shows clickable action chips that let you quickly navigate to relevant pages or perform common actions based on your conversation.",
  "category": "Improvement",
  "related_pages": ["/guide"],
  "created_by": "Platform Team",
  "published_at": "2024-12-08T11:00:00Z"
}
```

### 4. Azure SQL Database Support
```json
{
  "title": "Azure SQL Database Support",
  "description": "Fixed connection issues with Azure SQL databases in the Budget & Licensing section. Resource costs and licensing data now load reliably.",
  "category": "Bug Fix",
  "related_pages": ["/budget"],
  "created_by": "Platform Team",
  "published_at": "2024-12-06T16:00:00Z"
}
```

### 5. Budget Dashboard with Resource Group Selection
```json
{
  "title": "Budget Dashboard with Resource Group Selection",
  "description": "The Budget & Licensing page now lets you select specific Azure resource groups to view costs and resources. Filter by subscription and resource group for more targeted insights.",
  "category": "New Feature",
  "related_pages": ["/budget"],
  "created_by": "Platform Team",
  "published_at": "2024-12-04T15:00:00Z"
}
```

### 6. User Authentication & Access Control
```json
{
  "title": "User Authentication & Access Control",
  "description": "Added secure login with Microsoft Entra ID. Admins can now manage user access through the User Management page and approve access requests.",
  "category": "New Feature",
  "related_pages": ["/admin/users", "/admin/access-requests"],
  "created_by": "Platform Team",
  "published_at": "2024-12-04T10:00:00Z"
}
```

### 7. AI Guide Knows the Platform
```json
{
  "title": "AI Guide Knows the Platform",
  "description": "The AI Guide now has full knowledge of the Fourth AI Architecture platform. Ask it questions about governance, proposals, agents, or any other feature and get accurate, helpful answers.",
  "category": "New Feature",
  "related_pages": ["/guide"],
  "created_by": "Platform Team",
  "published_at": "2024-12-02T14:00:00Z"
}
```

### 8. Feedback Hub for Bug Reports & Ideas
```json
{
  "title": "Feedback Hub for Bug Reports & Ideas",
  "description": "New Feedback Hub where you can submit bug reports, feature requests, and general feedback. Track the status of your submissions and see what others have suggested.",
  "category": "New Feature",
  "related_pages": ["/feedback"],
  "created_by": "Platform Team",
  "published_at": "2024-12-02T11:00:00Z"
}
```

### 9. Enhanced Task Kanban Board
```json
{
  "title": "Enhanced Task Kanban Board",
  "description": "The Tasks page now features an improved Kanban board with drag-and-drop functionality, overdue task highlighting, and smoother animations.",
  "category": "Improvement",
  "related_pages": ["/tasks"],
  "created_by": "Platform Team",
  "published_at": "2024-12-02T09:00:00Z"
}
```

---

## Deployment Script

Run after production deployment:

```bash
API_URL="https://agent-arch-api.icyplant-75ca2495.westeurope.azurecontainerapps.io"

# Copy each JSON block above and POST:
curl -X POST "$API_URL/api/feature-updates" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

Or use the admin UI at `/updates` to create entries manually.
