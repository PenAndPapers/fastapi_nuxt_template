---
name: plan
description: Procedure for creating technical specifications and breakdown plans. Trigger when starting a new feature or major refactor.
---

# Feature Planning Procedure

## Step 1: Draft Technical Spec
Create a new file in `docs/plans/YYYY-MM-DD-<feature-name>.md` with the following structure:
```markdown
# [Feature Name] Technical Spec

## 1. Data Contracts
- Define backend request/response models.
- Map fields to Frontend TypeScript interfaces.

## 2. API Endpoints
- List path, method, input validation rules, and error status codes.

## 3. Database Changes
- List new tables, modified columns, and required Alembic migrations.